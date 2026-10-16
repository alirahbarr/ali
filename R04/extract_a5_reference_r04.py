#!/usr/bin/env python3
"""Reproduce A5 source-ink reference exports; never repair/snap source geometry."""
from pathlib import Path
import hashlib,json,math,collections,xml.etree.ElementTree as ET
import fitz
import ezdxf
from ezdxf.enums import TextEntityAlignment
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'01_Source_Drawings_and_References/348 Front newst Drawing.pdf'
OUT=ROOT/'06_CAD_and_3D_Models'
S=64*25.4/72
OX,OY=445.32,212.46
CROP=fitz.Rect(330,70,1150,625)
TOL=.5  # mm, cubic-to-polyline deviation criterion
DATE='2026-10-16'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def point(p,rotation):
 q=fitz.Point(p)*rotation
 return ((q.x-OX)*S,-(q.y-OY)*S)
def dist(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1]
 if dx*dx+dy*dy<1e-20:return math.hypot(p[0]-a[0],p[1]-a[1])
 t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def mid(a,b):return ((a[0]+b[0])/2,(a[1]+b[1])/2)
def cubic(a,b,c,d,depth=0):
 if depth>=20 or max(dist(b,a,d),dist(c,a,d))<=TOL:return [a,d]
 ab,bc,cd=mid(a,b),mid(b,c),mid(c,d)
 abc,bcd=mid(ab,bc),mid(bc,cd);m=mid(abc,bcd)
 return cubic(a,ab,abc,m,depth+1)[:-1]+cubic(m,bcd,cd,d,depth+1)
def clipseg(a,b,box):
 xmin,ymin,xmax,ymax=box;dx,dy=b[0]-a[0],b[1]-a[1];u,v=0.,1.
 for p,q in [(-dx,a[0]-xmin),(dx,xmax-a[0]),(-dy,a[1]-ymin),(dy,ymax-a[1])]:
  if abs(p)<1e-15:
   if q<0:return None
  else:
   r=q/p
   if p<0:u=max(u,r)
   else:v=min(v,r)
   if u>v:return None
 return ((a[0]+u*dx,a[1]+u*dy),(a[0]+v*dx,a[1]+v*dy))
def main():
 OUT.mkdir(exist_ok=True);before=digest(SRC)
 source=fitz.open(SRC);pg=source[0];rotation=pg.rotation_matrix
 drawings=pg.get_drawings()
 lo=((CROP.x0-OX)*S,-(CROP.y1-OY)*S);hi=((CROP.x1-OX)*S,-(CROP.y0-OY)*S)
 box=(*lo,*hi)
 doc=ezdxf.new('R2010');doc.units=4;doc.header['$MEASUREMENT']=1
 for name,color in [('SOURCE_TRACE',8),('SOURCE_TEXT',7),('REFERENCE_NOTES',1)]:doc.layers.new(name,dxfattribs={'color':color})
 ms=doc.modelspace();counts=collections.Counter();omitted_text=[];fonts=set()
 def inside(p):return box[0]-1e-7<=p[0]<=box[2]+1e-7 and box[1]-1e-7<=p[1]<=box[3]+1e-7
 def emitline(a,b):
  cc=clipseg(a,b,box)
  if cc and math.dist(*cc)>1e-7:ms.add_line(*cc,dxfattribs={'layer':'SOURCE_TRACE'});counts['line_entities']+=1
 def emitpoly(points,closed=False):
  if all(inside(p) for p in points):
   ms.add_lwpolyline(points,close=closed,dxfattribs={'layer':'SOURCE_TRACE'});counts['polyline_entities']+=1
  else:
   for a,b in zip(points,points[1:]+([points[0]] if closed else [])):emitline(a,b)
 for dr in drawings:
  rr=dr['rect']*rotation
  if rr.x1<CROP.x0 or rr.x0>CROP.x1 or rr.y1<CROP.y0 or rr.y0>CROP.y1:continue
  counts['intersecting_source_paths']+=1
  if dr.get('fill') is not None:counts['source_filled_paths_outlined_in_dxf']+=1
  for item in dr['items']:
   kind=item[0];counts['source_primitive_'+kind]+=1
   if kind=='l':emitline(point(item[1],rotation),point(item[2],rotation))
   elif kind=='c':emitpoly(cubic(*(point(v,rotation) for v in item[1:5])))
   elif kind=='re':
    r=item[1];emitpoly([point(v,rotation) for v in [r.tl,r.tr,r.br,r.bl]],True)
   elif kind=='qu':
    q=item[1];emitpoly([point(v,rotation) for v in [q.ul,q.ur,q.lr,q.ll]],True)
   else:raise RuntimeError('Unrecognized source primitive: '+kind)
 # Separate editable text layer. Baseline/FIT endpoints preserve source spans;
 # CAD font substitution can alter glyphs; SVG outlines remain visual authority.
 for block in pg.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   dx,dy=line['dir'];vx,vy=dy,dx
   for sp in line['spans']:
    rr=fitz.Rect(sp['bbox'])*rotation;text=sp['text']
    if not text.strip() or not rr.intersects(CROP):continue
    if not CROP.contains(rr):omitted_text.append(text);continue
    fonts.add(sp['font']);start=point(sp['origin'],rotation)
    advance=(rr.width if abs(vx)>abs(vy) else rr.height)*S
    height=max(.1,sp['size']*max(.5,min(1.0,sp.get('ascender',.73)))*S)
    end=(start[0]+vx*advance,start[1]+vy*advance)
    ent=ms.add_text(text,dxfattribs={'layer':'SOURCE_TEXT','height':height})
    if advance>.1:ent.set_placement(start,end,align=TextEntityAlignment.FIT)
    else:ent.set_placement(start)
    counts['text_entities']+=1
 notes=[
 'R04 A5 REFERENCE TRACE - SOURCE INK ONLY - NOT A SURVEY',
 'NOT FOR CONSTRUCTION OR SET-OUT - uniform nominal 1:64; millimetres; XY up',
 'Source A5 2026-06-19; issued reference 2026-10-16; no snapping or dimension-chain repair',
 'Cubic curves approximated <=0.5mm criterion; filled shapes outlined; SVG preserves original appearance',
 ]
 for i,txt in enumerate(notes):ms.add_text(txt,dxfattribs={'layer':'REFERENCE_NOTES','height':120}).set_placement((box[0],box[3]+900-i*200))
 dxf=OUT/'R04_A5_Reference.dxf';doc.saveas(dxf)
 check=ezdxf.readfile(dxf);audit=check.audit()
 if audit.errors:raise RuntimeError('DXF audit failed:'+str(audit.errors))
 # SVG: displayed source export already includes PDF rotation. Outer nested SVG
 # clips a copy; source paths/text outlines are not rewritten or stretched.
 ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns);ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
 source_svg=ET.fromstring(pg.get_svg_image(text_as_path=True))
 outer=ET.Element('{%s}svg'%ns,{'width':str(CROP.width),'height':str(CROP.height+55),'viewBox':f'0 0 {CROP.width} {CROP.height+55}'})
 metadata=ET.SubElement(outer,'{%s}metadata'%ns);metadata.text=json.dumps({'source_sha256':before,'display_crop_pt':list(CROP),'mm_per_display_pt':S,'cad_origin_display_pt':[OX,OY],'cad_mapping':'X=(x-445.32)*S;Y=-(y-212.46)*S','status':'SOURCE INK REFERENCE;NOT SURVEY;NOT FOR CONSTRUCTION'})
 ET.SubElement(outer,'{%s}rect'%ns,{'width':'100%','height':'100%','fill':'white'})
 for yy,txt in [(17,'R04 / A5 SOURCE REFERENCE - NOT SURVEY - NOT FOR CONSTRUCTION'),(35,'Uniform nominal1:64 mapping only; original dimension-chain conflict retained; 16 October2026')]:
  t=ET.SubElement(outer,'{%s}text'%ns,{'x':'10','y':str(yy),'font-family':'sans-serif','font-size':'12','fill':'#783b2c'});t.text=txt
 source_svg.set('x','0');source_svg.set('y','55');source_svg.set('width',str(CROP.width));source_svg.set('height',str(CROP.height));source_svg.set('viewBox',f'{CROP.x0} {CROP.y0} {CROP.width} {CROP.height}');source_svg.set('overflow','hidden')
 defs=ET.SubElement(outer,'{%s}defs'%ns);cp=ET.SubElement(defs,'{%s}clipPath'%ns,{'id':'r04_reference_viewport'});ET.SubElement(cp,'{%s}rect'%ns,{'x':'0','y':'0','width':str(CROP.width),'height':str(CROP.height)})
 source_svg.set('y','0');wrapper=ET.SubElement(outer,'{%s}g'%ns,{'transform':'translate(0,55)','clip-path':'url(#r04_reference_viewport)'});wrapper.append(source_svg)
 svg=OUT/'R04_A5_Reference.svg';ET.ElementTree(outer).write(svg,encoding='utf-8',xml_declaration=True)
 # Round-trip geometry: imported DXF endpoints must agree with extracted controls.
 controls=[(445.32,144.12),(1047.54,144.12),(716.52,502.86),(792.18,212.46),(569.88,241.32)]
 vertices=[]
 for en in check.modelspace():
  if en.dxf.layer!='SOURCE_TRACE':continue
  if en.dxftype()=='LINE':vertices.extend([(en.dxf.start.x,en.dxf.start.y),(en.dxf.end.x,en.dxf.end.y)])
  elif en.dxftype()=='LWPOLYLINE':vertices.extend([(v[0],v[1]) for v in en.get_points()])
 residuals=[]
 for xx,yy in controls:
  target=((xx-OX)*S,-(yy-OY)*S);delta=min(math.dist(target,v) for v in vertices)
  residuals.append({'display_pt':[xx,yy],'mapped_xyup_mm':target,'nearest_export_vertex_mm':delta})
 if max(x['nearest_export_vertex_mm'] for x in residuals)>2:raise RuntimeError('Control export residual above2mm')
 bounds=[min(x for x,y in vertices),min(y for x,y in vertices),max(x for x,y in vertices),max(y for x,y in vertices)]
 if any(a<b-1e-5 for a,b in zip(bounds[:2],box[:2])) or any(a>b+1e-5 for a,b in zip(bounds[2:],box[2:])):raise RuntimeError('Clipping bounds failed')
 preview_status='not requested'
 try:
  svgd=fitz.open(svg);svgd[0].get_pixmap(matrix=fitz.Matrix(2,2)).save(OUT/'R04_A5_Reference_Preview.png')
  import os;os.environ.setdefault('MPLCONFIGDIR','/tmp/348-front-matplotlib')
  from ezdxf.addons.drawing import RenderContext,Frontend
  from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  fig=plt.figure(figsize=(16,12));ax=fig.add_axes([.01,.01,.98,.98]);ax.set_aspect('equal')
  Frontend(RenderContext(check),MatplotlibBackend(ax)).draw_layout(check.modelspace(),finalize=True)
  fig.savefig(OUT/'R04_A5_DXF_Roundtrip.png',dpi=130);plt.close(fig)
  preview_status='SVG opened/rendered byPyMuPDF;DXF reread/rendered byezdxf+matplotlib'
 except ImportError as exc:preview_status='Optional preview dependency missing:'+str(exc)
 after=digest(SRC)
 if before!=after:raise RuntimeError('Source hash changed')
 meta={'revision':'R04','issue_date_toronto':DATE,'source_file':str(SRC.relative_to(ROOT)),'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'source_rotation':pg.rotation,'display_crop_pt':list(CROP),'crop_reason':'Keeps front width dimension,door swing,source controls;excludes separate cooking-line view and title block','scale':'UNIFORM NOMINAL1:64;NOT SURVEY;NOT CONSTRUCTION','mm_per_display_pt':S,'display_origin_pt':[OX,OY],'dxf_mapping':'X=(displayX-445.32)*S;Y=-(displayY-212.46)*S','svg_mapping':'Original displayed PDF points in nested crop;mm transform recorded in SVG metadata;no second rotation','dxf_layers':['SOURCE_TRACE','SOURCE_TEXT','REFERENCE_NOTES'],'dxf_units':4,'dxf_units_description':'millimetres','dxf_version':check.dxfversion,'curve_approximation':{'method':'adaptive cubic de Casteljau subdivision;control-point distance to chord <= tolerance','tolerance_mm':TOL,'max_depth':20,'scope':'DXF cubic curves only;SVG preserves original Beziers'},'fill_policy':'DXF filled source paths retain outline geometry;SVG retains source fills,clipping and text glyph outlines','text_policy':'DXF editable text with source baseline/FIT endpoints and cap-height approximation;CAD font substitution can differ;SVG is visual source-text authority','source_fonts':sorted(fonts),'partially_cropped_text_omitted_from_dxf':omitted_text,'source_path_count':len(drawings),'counts':dict(counts),'dxf_audit':{'errors':len(audit.errors),'fixes':len(audit.fixes)},'source_trace_xyup_mm_bounds':bounds,'expected_crop_xyup_mm_bounds':box,'control_roundtrip_checks':residuals,'written_dimension_discrepancy_retained_mm':12.7,'reference_not_new_layout':True,'previews':preview_status,'outputs':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in [dxf,svg]}}
 (OUT/'R04_A5_Extraction_Metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
 print(json.dumps({'outputs':[str(dxf),str(svg)],'counts':dict(counts),'audit':meta['dxf_audit'],'max_control_residual_mm':max(x['nearest_export_vertex_mm'] for x in residuals),'source_unchanged':before==after,'previews':preview_status},indent=2))
if __name__=='__main__':main()
