#!/usr/bin/env python3
"""R04: consistent unsized component geometry and source-based review sheets.

No photograph scaling and no inferred site heights. All component projections
and the OBJ use the exact same normalized vertices. A5 stays an independent
millimetre reference trace; the component is deliberately not inserted into it.
"""
from pathlib import Path
import os
import hashlib
import json
import math
import zipfile
import numpy as np
import pymupdf
os.environ.setdefault('MPLCONFIGDIR','/tmp/348-front-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/348-front-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from matplotlib.colors import to_rgb
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT/'06_CAD_and_3D_Models'
OUT = ROOT/'R04_Development'
W,H = 1152,792
DATE = '16 October 2026'
INK='#283C37'; BRICK='#B66B48'; GREY='#B6B2A9'; PALE='#F7F4EE'
P = dict(outer_width=1.0, outer_height=.92, depth=.32,
         outer_radius=.04, opening_width=.60, opening_top=.805,
         opening_radius=.105, counter_width=.57, counter_back_y=.14,
         counter_bow=.17, counter_height=.33, worktop_thickness=.012,
         screen_front_y=.30, screen_thickness=.018)
PARTS={}

def profile(half, top, radius):
    left=[]
    for z in np.linspace(0,top-radius,9): left.append((-half,float(z)))
    for a in np.linspace(math.pi, math.pi/2,9)[1:]:
        left.append((-half+radius+radius*math.cos(a),top-radius+radius*math.sin(a)))
    middle=[(float(x),top) for x in np.linspace(-half+radius,half-radius,7)[1:]]
    right=[(-x,z) for x,z in left[-2::-1]]
    return left+middle+right

def frame_mesh(outer, inner, depth):
    v=[]; f=[]
    for (xo,zo),(xi,zi) in zip(outer,inner):
        v.extend([[xo,0,zo],[xo,depth,zo],[xi,0,zi],[xi,depth,zi]])
    for i in range(len(outer)-1):
        a=4*i; b=a+4
        f.extend([[a,a+2,b+2,b],[a+1,b+1,b+3,a+3],
                  [a,b,b+1,a+1],[a+2,a+3,b+3,b+2]])
    f.extend([[0,1,3,2],[len(v)-4,len(v)-2,len(v)-1,len(v)-3]])
    return v,f

def prism(poly,z0,z1):
    n=len(poly); v=[[x,y,z0] for x,y in poly]+[[x,y,z1] for x,y in poly]
    f=[list(range(n-1,-1,-1)),list(range(n,2*n))]
    f += [[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
    return v,f

def box(x0,x1,y0,y1,z0,z1):
    return prism([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1)

def model():
    outer=profile(.5,P['outer_height'],P['outer_radius'])
    inner=profile(.3,P['opening_top'],P['opening_radius'])
    PARTS['portal_brick']={'material':'brick','mesh':frame_mesh(outer,inner,P['depth'])}
    curve=[(.285*math.cos(a),.14+.17*math.sin(a)) for a in np.linspace(math.pi,2*math.pi,49)]
    PARTS['cashier_face']={'material':'brick','mesh':prism(curve,0,.33)}
    PARTS['worktop']={'material':'dark_top','mesh':prism(curve,.33,.342)}
    PARTS['opaque_backing']={'material':'mineral','mesh':box(-.30,.30,.30,.318,0,.805)}
    PARTS['finished_top_component_only']={'material':'mineral','mesh':box(-.46,.46,.015,.32,.9202,.927)}
    data={'revision':'R04','date':DATE,'status':'UNSIZED COMPONENT DESIGN STUDY',
          'units':'normalized display units; width=1; not metres or millimetres',
          'physical_scale_mm':None,'host_plan_placement':None,'site_heights':None,
          'coordinates':'X left/right; Y rearward; Z up; public front Y<0; component base Z=0',
          'parameters':P,'outer_profile_xz':outer,'opening_profile_xz':inner,
          'counter_outline_xy':curve,'parts':{},
          'limits':['No site fit or actual heights','No staff opening fitted in backing',
                    'No accessible transaction detail yet','No full kitchen roof extent',
                    'Top non-walkable; support/fixing/assembly unengineered',
                    'Solid finish envelopes only; not fabrication meshes'],
          'geometry_policy':'Same vertices/parameters generate OBJ, front, local plan, section and axonometric; no separate AI views'}
    obj=['# R04 UNSIZED COMPONENT ONLY; normalized width=1',
         '# No physical units or host placement; DO NOT IMPORT AS MM/METRES',
         'mtllib R04_Portal_Component.mtl']
    offset=1
    for name,d in PARTS.items():
        vertices,faces=d['mesh']; data['parts'][name]={'material':d['material'],'vertices':vertices,'faces_zero_based':faces}
        obj += ['o '+name,'usemtl '+d['material']]
        obj += ['v '+' '.join(f'{c:.8f}' for c in v) for v in vertices]
        obj += ['f '+' '.join(str(i+offset) for i in face) for face in faces]
        offset+=len(vertices)
    (CAD/'R04_Portal_Component.obj').write_text('\n'.join(obj)+'\n')
    (CAD/'R04_Portal_Component.mtl').write_text('newmtl brick\nKd .71 .42 .28\n\nnewmtl dark_top\nKd .20 .22 .21\n\nnewmtl mineral\nKd .69 .68 .63\n')
    (CAD/'R04_Portal_Component.json').write_text(json.dumps(data,indent=2))
    return data

def axon(data):
    """Orthographic CAD rendering with a depth buffer (no painter-sort errors)."""
    from PIL import Image
    colors={'brick':BRICK,'dark_top':'#343A37','mineral':GREY}
    view=np.array([1.3,-2.5,1.8]);view/=np.linalg.norm(view)
    right=np.cross(np.array([0.,0.,1.]),view);right/=np.linalg.norm(right)
    up=np.cross(view,right)
    basis=np.array([right,up,view])
    allv=np.concatenate([np.array(d['mesh'][0]) for d in PARTS.values()])
    projected=allv @ basis.T
    lo=projected[:,:2].min(axis=0);hi=projected[:,:2].max(axis=0)
    width,height=1440,1200;pad=70
    scale=min((width-2*pad)/(hi[0]-lo[0]),(height-2*pad)/(hi[1]-lo[1]))
    def project(v):
        q=v @ basis.T
        q[:,0]=(q[:,0]-(lo[0]+hi[0])/2)*scale+width/2
        q[:,1]=height/2-(q[:,1]-(lo[1]+hi[1])/2)*scale
        return q
    pixels=np.zeros((height,width,3),dtype=np.uint8)
    pixels[:]=np.array(to_rgb(PALE))*255
    depth=np.full((height,width),-np.inf)
    light=np.array([-.4,-.6,.7]);light/=np.linalg.norm(light)
    count=0
    for name,d in PARTS.items():
        vertices,faces=d['mesh'];v=np.array(vertices);q=project(v)
        for face in faces:
            normal=np.cross(v[face[1]]-v[face[0]],v[face[2]]-v[face[0]])
            normal/=max(np.linalg.norm(normal),1e-12)
            if np.dot(normal,view)<=0:continue
            shade=.68+.32*max(0,float(np.dot(normal,light)))
            rgb=np.array(to_rgb(colors[d['material']]))*shade*255
            for i in range(1,len(face)-1):
                a,b,cc=q[[face[0],face[i],face[i+1]]]
                x0=max(0,int(np.floor(min(a[0],b[0],cc[0]))));x1=min(width-1,int(np.ceil(max(a[0],b[0],cc[0]))))
                y0=max(0,int(np.floor(min(a[1],b[1],cc[1]))));y1=min(height-1,int(np.ceil(max(a[1],b[1],cc[1]))))
                if x1<x0 or y1<y0:continue
                xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
                den=(b[1]-cc[1])*(a[0]-cc[0])+(cc[0]-b[0])*(a[1]-cc[1])
                if abs(den)<1e-10:continue
                u=((b[1]-cc[1])*(xx-cc[0])+(cc[0]-b[0])*(yy-cc[1]))/den
                vv=((cc[1]-a[1])*(xx-cc[0])+(a[0]-cc[0])*(yy-cc[1]))/den
                ww=1-u-vv
                zz=u*a[2]+vv*b[2]+ww*cc[2]
                zlocal=depth[y0:y1+1,x0:x1+1]
                mask=(u>=-1e-9)&(vv>=-1e-9)&(ww>=-1e-9)&(zz>zlocal)
                zlocal[mask]=zz[mask];pixels[y0:y1+1,x0:x1+1][mask]=rgb
                count+=1
    Image.fromarray(pixels).save(OUT/'R04_Above_View.png')
    assert count>0

def font_setup():
    for name,file in [('D','DejaVuSans.ttf'),('DB','DejaVuSans-Bold.ttf')]:
        pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))

def para(c,text,x,top,width,size=12,color=INK):
    style=ParagraphStyle('p',fontName='D',fontSize=size,leading=size*1.42,textColor=HexColor(color))
    p=Paragraph(text,style); w,h=p.wrap(width,1000); p.drawOn(c,x,top-h); return h

def label(c,text,x,y,size=11,bold=False,color=INK):
    c.setFillColor(HexColor(color)); c.setFont('DB' if bold else 'D',size); c.drawString(x,y,text)

def header(c,num,title,sub):
    c.setFillColor(HexColor(PALE));c.rect(0,0,W,H,fill=1,stroke=0)
    label(c,'348 FRONT / RESTAURANT DESIGN DEVELOPMENT',40,755,12,True)
    label(c,title,40,712,27,True);para(c,sub,40,688,1072,12)
    c.setStrokeColor(HexColor('#C9C8BF'));c.line(40,44,1112,44)
    label(c,f'R04 / {num:02d}     {DATE} · Toronto',40,25,9)
    label(c,'COORDINATION STUDY · NOT FOR CONSTRUCTION',782,25,9,True)

def poly(c,pts,fill=BRICK,stroke=INK,width=.8):
    p=c.beginPath();p.moveTo(*pts[0])
    for x,y in pts[1:]:p.lineTo(x,y)
    p.close(); c.setLineWidth(width); c.setStrokeColor(HexColor(stroke));c.setFillColor(HexColor(fill));c.drawPath(p,fill=1,stroke=1)

def front(c,data,x,y,s):
    outer=data['outer_profile_xz'];inner=data['opening_profile_xz']
    trans=lambda p:(x+p[0]*s,y+p[1]*s)
    poly(c,[trans(p) for p in outer]+[trans(p) for p in inner[::-1]])
    poly(c,[(x-.30*s,y),(x+.30*s,y),(x+.30*s,y+.805*s),(x-.30*s,y+.805*s)],GREY)
    # Repaint the frame over the opaque plane, preserving its actual profile.
    poly(c,[trans(p) for p in outer]+[trans(p) for p in inner[::-1]])
    poly(c,[(x-.285*s,y),(x+.285*s,y),(x+.285*s,y+.33*s),(x-.285*s,y+.33*s)])
    poly(c,[(x-.285*s,y+.33*s),(x+.285*s,y+.33*s),(x+.285*s,y+.342*s),(x-.285*s,y+.342*s)],'#343A37')
    c.setStrokeColor(HexColor('#D6C2A8'));c.setLineWidth(.5)
    # A texture cue only, not a brick set-out or product module.
    for z in np.arange(.04,.92,.035):
        for xa,xb in [(-.5,-.30),(.30,.5)]:
            if z<.88:c.line(x+xa*s,y+z*s,x+xb*s,y+z*s)
    c.setStrokeColor(HexColor(INK));c.line(x-.60*s,y,x+.60*s,y)

def plan(c,data,x,y,s):
    # Local plan above the counter; source/store coordinates are not implied.
    for xa,xb in [(-.5,-.3),(.3,.5)]:
        poly(c,[(x+xa*s,y),(x+xb*s,y),(x+xb*s,y+.32*s),(x+xa*s,y+.32*s)])
    poly(c,[(x-.3*s,y+.30*s),(x+.3*s,y+.30*s),(x+.3*s,y+.318*s),(x-.3*s,y+.318*s)],GREY)
    poly(c,[(x+a*s,y+b*s) for a,b in data['counter_outline_xy']],'#343A37')
    c.setStrokeColor(HexColor('#7E8D7E'));c.setDash(4,3)
    c.rect(x-.50*s,y,1*s,.32*s,stroke=1,fill=0);c.setDash()
    label(c,'FRONT / GUEST',x-.17*s,y-.09*s,10,True)

def section(c,x,y,s):
    # Central longitudinal cut X=0, exactly P, not a building section.
    poly(c,[(x,y+.805*s),(x+.32*s,y+.805*s),(x+.32*s,y+.92*s),(x,y+.92*s)])
    poly(c,[(x+.015*s,y+.9202*s),(x+.32*s,y+.9202*s),(x+.32*s,y+.927*s),(x+.015*s,y+.927*s)],GREY)
    poly(c,[(x-.03*s,y),(x+.14*s,y),(x+.14*s,y+.33*s),(x-.03*s,y+.33*s)])
    poly(c,[(x-.03*s,y+.33*s),(x+.14*s,y+.33*s),(x+.14*s,y+.342*s),(x-.03*s,y+.342*s)],'#343A37')
    poly(c,[(x+.30*s,y),(x+.318*s,y),(x+.318*s,y+.805*s),(x+.30*s,y+.805*s)],GREY)
    c.setStrokeColor(HexColor(INK));c.line(x-.12*s,y,x+.43*s,y)

def table(c,rows,x,top,widths,rowh=60,size=10):
    y=top
    for row_i,row in enumerate(rows):
        rh=rowh if row_i else 32
        c.setFillColor(HexColor('#E4E9E2' if row_i==0 else ('#FFFFFF' if row_i%2 else '#F0EFE9')))
        c.rect(x,y-rh,sum(widths),rh,fill=1,stroke=0)
        xx=x
        for text,w in zip(row,widths):
            used=para(c,escape(text),xx+9,y-8,w-18,size if row_i else size+1)
            if used>rh-12:raise ValueError(f'Table overflow row {row_i}: {text}')
            xx+=w
        y-=rh
    return y

def pages(data):
    path=OUT/'R04_Design_Development.pdf'; c=canvas.Canvas(str(path),pagesize=(W,H))
    c.setTitle('R04 Restaurant design development — approved compact brick direction')
    header(c,1,'The approved brick direction, developed','Working documents: 352 Front Street West, Unit 105 · Customer entrance: 348 Front Street West')
    c.drawImage(str(ROOT/'07_Renderings/R03_V02_Compact_Form_Study.png'),40,165,width=745,height=497,preserveAspectRatio=True)
    label(c,'OWNER-SELECTED VISUAL BASIS: R03 V02',814,636,12,True)
    para(c,'Deep rounded opening, broad brick piers, curved cashier and opaque grey backing. Keep the floor flush.',814,610,295,13)
    label(c,'NEW IN THIS ISSUE',814,510,12,True)
    para(c,'A5 source control drawing and editable DXF.<br/><br/>One shared 3D component with matching plan, elevation, section and view from above.<br/><br/>Finish, service and measurement schedules.',814,484,295,12)
    para(c,'The component is an unsized design study. No site heights, physical scale or fitted staff entrance are assigned. This issue develops the selected design without treating a rendering as measured geometry.',814,285,295,11)
    para(c,'The supplied PDFs are the available base. The R03 image is AI generated; the R04 technical views are generated from the accompanying normalized component geometry.',40,137,735,11)
    c.showPage()

    header(c,2,'A5 / source controls and layout constraints','Original plan underlay, independently retained written dimensions and source trace. Frontage is LEFT; owner’s left wall is TOP.')
    # Source vector underlay is inserted below all canvas content after save.
    label(c,'1  Frontage',45,177,10,True);label(c,'2  A5 POS reference',230,177,10,True)
    label(c,'3  Mezzanine floor-limit line',459,177,10,True);label(c,'4  Retained universal WC',790,177,10,True)
    para(c,'Written: overall 13,601.7 mm; front width 6,159.5 mm; rear width 5,448.3 mm; frontage–POS 2,806.7 mm. Split lengths 6,121.4 + 7,467.6 = 13,589.0 mm, leaving a 12.7 mm conflict with the overall.',40,150,1072,11)
    para(c,'Keep the guest-right stair route independent. The rear/guest-left WC approach is unresolved. Preserve 2 coolers + 1 freezer on the confirmed left side. A5 equipment boxes are not new enclosure walls; the new portal is not inserted here until staff/public fit and site controls are resolved.',40,102,1072,11)
    c.showPage()

    header(c,3,'Cashier / matched front and local plan','Both views use the accompanying component JSON/OBJ. Normalized width = 1.00; no physical units, site placement or construction dimensions.')
    front(c,data,330,170,480)
    label(c,'FRONT ELEVATION',78,635,13,True)
    label(c,'BR-01  /  deep brick appearance',68,128,11)
    label(c,'CT-01  /  smooth dark worktop',68,107,11)
    label(c,'PN-01  /  opaque grey backing',68,86,11)
    label(c,'LOCAL COMPONENT PLAN',680,635,13,True)
    plan(c,data,875,320,390)
    para(c,'Solid: piers, curved counter and opaque screen.<br/>Dashed: roof extent above this component only.<br/><br/>The back recess expresses intended working space. Its width/depth and a concealed kitchen-side entry remain to be fitted. No door or accessible transaction position is falsely shown as resolved.',664,253,429,12)
    c.showPage()

    header(c,4,'Soffit, backing and the finished top','Central longitudinal component cut and view from above share the same geometry. This is not a measured section through the shop or mezzanine.')
    label(c,'CENTRAL SECTION / X = 0',55,633,13,True)
    section(c,160,155,480)
    label(c,'BR-02  overhead return',50,114,11)
    label(c,'TP-01  finished top',50,93,11)
    para(c,'No raised threshold. The staff band between counter and backing still needs a fitted entry and dimensional review.',50,75,420,10)
    c.drawImage(str(OUT/'R04_Above_View.png'),465,188,width=630,height=450,preserveAspectRatio=True,mask='auto')
    para(c,'The grey cap is a proposed finish on the component top, visible from above. Extend it to the actual kitchen roof only after its extent is fixed. The view is an axonometric, not a verified seated mezzanine sightline.',545,165,550,11)
    para(c,'Design separate load paths for decoration, kitchen enclosure and existing mezzanine. Use a reviewed overhead system with positive retention. Top: non-walkable, no storage; provide a safe cleaning/access method.',545,103,550,11)
    c.showPage()

    header(c,5,'Service and circulation / develop in this order','Functional relationship diagram only. Boxes and arrows do not represent available floor area, door locations or a solved public washroom route.')
    blocks=[(50,395,245,145,'ARRIVAL / PUBLIC','Order, payment and pickup\nGround dining target: 5–6'),
            (365,395,300,145,'CASHIER / SCREEN','Curved counter + opaque backing\nSeparate payment and pickup'),
            (735,395,365,145,'ENCLOSED KITCHEN','Screened internal staff/dispatch link\nStaff entry to be located'),
            (50,175,430,135,'GUEST-RIGHT ROUTE','Independent approach to stair / mezzanine\nNo fixed queue, stores or staff-door conflict'),
            (660,175,440,135,'REAR UNIVERSAL WASHROOM','Retained in current baseline\nIndependent public approach still unresolved')]
    for x,y,w,h,title,body in blocks:
        c.setFillColor(HexColor('#E7E8DF'));c.roundRect(x,y,w,h,10,fill=1,stroke=0)
        label(c,title,x+16,y+h-30,12,True)
        para(c,body.replace('\n','<br/>'),x+16,y+h-50,w-32,12)
    for xa,xb,y in [(295,365,467),(665,735,467)]:
        c.setStrokeColor(HexColor(INK));c.setLineWidth(2);c.line(xa+5,y,xb-8,y)
        poly(c,[(xb-8,y),(xb-18,y+5),(xb-18,y-5)],INK)
    para(c,'1. Fit staff access and screened order transfer behind the cashier.<br/>2. Fit accessible payment, pickup and the expected queue together.<br/>3. Resolve the WC/public connection alongside the stair route.<br/>4. Then fix portal width, depth, screen offset and roof projection.',50,140,1050,12)
    c.showPage()

    header(c,6,'Materials / spend where the design is seen','Preferred design basis. Candidate systems remain subject to substrate, cleaning, slip, fire, load and installation evidence for their actual use.')
    rows=[['ID / zone','Development choice','Cost and technical control'],
          ['BR-01 / BR-02\nPortal and soffit','Warm clay-brick appearance with light joints. Continuous piers and deep returns.','Keep brick concentrated on the feature. Overhead system needs engineered retention; vertical slips are not automatically suitable.'],
          ['CT-01 / PN-01 / TP-01\nCounter, backing, top','Smooth dark worktop; quiet opaque grey screen; cleanable mineral-grey upper surface.','Prioritize workable staff entry, transaction detail and service access over hidden decorative brick.'],
          ['FL-G01\nGround public floor','Test the already exposed substrate for a retained concrete finish. Matte concrete-look porcelain is the fallback.','No repeat tile-removal allowance. Check moisture, cracks, levels, slip and thresholds before selecting the system.'],
          ['FL-K01 / KW-01 / KW-02\nKitchen','Suitable concrete-look commercial tile; stainless at hot/greasy/splash zones; hygienic system elsewhere.','Price by exposure zone. Resolve coves, joints and substrate; metal does not upgrade an unsuitable backing.'],
          ['WF-01 / WF-02\nPublic walls','Washable warm-grey paint as the economical base. Limit specialist mineral texture to a feature surface.','Sample the look first. Do not assume raw cement or limewash will be economical, durable or easy to clean.'],
          ['FL-S01 / FL-M01\nStair and mezzanine','Coherent concrete appearance using a system suited to each actual assembly.','Survey complete stair and landings; verify upstairs load/movement. Do not assume a polishable concrete floor or add a new pour.'],
          ['FF-01 / TX-01 / AC-01\nUpstairs dining','Simple brown wood furniture, restrained Persian textile and tested acoustic absorption.','Fit seats and clear routes before purchasing. Secure any rug; keep stairs clear. Retain useful acoustic scope.']]
    table(c,rows,40,638,[200,375,497],rowh=73,size=10)
    c.showPage()

    header(c,7,'The measurements that unlock the fitted design','Use the supplied PDFs now; collect the following site controls for the next fitted plan and vertical model. A new DWG is not assumed available.')
    rows=[['Control set','Record on site / from responsible designer','What it fixes'],
          ['M-01 / plan coordinates','Storefront, clear entry, inside wall faces, columns, actual TV fascia and mezzanine edge. Tie them to a common datum.','Portal position; entry/queue; correct relation between old fascia and actual floor limit.'],
          ['M-02 / levels and overheads','Ground finished level, underside/top of mezzanine, lowest beam/duct/hood/services, guard top and intended kitchen ceiling.','Height/depth of the portal; roof/top extent; service access; actual mezzanine view.'],
          ['M-03 / staff + equipment','Selected equipment cut sheets, opening/ventilation/removal envelopes, service points, desired staff entry and order transfer.','Left-wall refrigeration fit; kitchen enclosure; viable cashier work recess.'],
          ['M-04 / public facilities','Actual corridor, stair and washroom doors/swings, landings, all stair treads/risers and guard/handrail positions.','Public WC connection, guest route, dining/transaction accessibility, complete stair finish design.'],
          ['M-05 / floor and supports','Ground slab/screed identity, moisture/cracks, floor build-ups, upstairs framing/deflection and verified support locations.','Appropriate concrete-look systems; transitions; engineered overhead/decorative attachment.']]
    table(c,rows,40,638,[190,535,347],rowh=90,size=11)
    para(c,'Also obtain the current accepted drawing/permit record and the actual CAD 102,000 + tax HVAC/ecology/gas quotation. No new project total, ordering release or construction progress is inferred in R04.',40,133,1072,12)
    c.showPage()

    header(c,8,'What the files contain / next coordination issue','The approved visual direction is recorded. The source reference, unsized component and later fitted restaurant model have distinct roles.')
    rows=[['File','Purpose / units'],
          ['R04_Design_Development.pdf + PNG sheets','Reviewable source-control and coordinated component views; finish, operation and measurement schedules.'],
          ['R04_A5_Reference.dxf / .svg','Editable reference extraction from A5. DXF in nominal model millimetres, 1:1, derived from source print scale 1:64; source ink only, not a survey. No stretched dimension-chain repair.'],
          ['R04_Portal_Component.obj + .mtl + .json','One shared component geometry. Unitless normalized width = 1; physical_scale_mm = null. Do not import as metres/mm or substitute for fitted CAD.'],
          ['R04_Planning_Basis.md / control anchors JSON','Source trace, written dimensions, residuals and retained layout constraints.'],
          ['R04_Design_Development_Schedule.md','Detailed finish IDs, staff/service strategy, lighting, acoustics, evidence and trade coordination sequence.']]
    table(c,rows,40,638,[390,682],rowh=68,size=11)
    para(c,'Next fitted issue: measured base + equipment, closed kitchen/public WC strategy, actual staff entry, accessible transaction, seating and queue, then complete roof/portal sections and independent support. The normalized component is adjustable when those controls are known.',40,235,1072,12)
    para(c,'Retained facts: only ground-floor tile/adhesive removal reported; refrigeration = 2 coolers + 1 freezer on the LEFT when entering; retained ground WC; future storage/extra upstairs WC separate and unapproved; no curved brick upper-mezzanine ceiling edge.',40,162,1072,11)
    para(c,'Delivery: use the private GitHub R04 folder while signed into the authorized account. The iPhone Safari workaround and concise app/support instructions are supplied separately.',40,94,1072,11)
    c.showPage();c.save()
    # Insert original source vectors on sheet02, under the callouts/notes.
    d=pymupdf.open(path); source=pymupdf.open(ROOT/'01_Source_Drawings_and_References/348 Front newst Drawing.pdf')
    source[0].remove_rotation(); clip=pymupdf.Rect(385,165,1115,520)
    target=pymupdf.Rect(40,140,1112,601)
    # show_pdf_page preserves aspect ratio; calculate the actual fitted rectangle.
    scale=min(target.width/clip.width,target.height/clip.height)
    tw,th=clip.width*scale,clip.height*scale
    actual=pymupdf.Rect(target.x0+(target.width-tw)/2,target.y0+(target.height-th)/2,target.x0+(target.width+tw)/2,target.y0+(target.height+th)/2)
    d[1].show_pdf_page(actual,source,0,clip=clip,overlay=True)
    for num,(sx,sy) in enumerate([(445.32,350),(569.88,241.32),(792.18,212.46),(1015,242)],1):
        px=actual.x0+(sx-clip.x0)*scale; py=actual.y0+(sy-clip.y0)*scale
        d[1].draw_circle((px,py),9,color=(.16,.24,.22),fill=(.16,.24,.22),overlay=True)
        d[1].insert_text((px-3,py+4),str(num),fontsize=11,color=(1,1,1),fontname='hebo',overlay=True)
    updated=path.with_suffix('.tmp.pdf');d.save(updated,garbage=4,deflate=True);d.close();updated.replace(path)
    d=pymupdf.open(path)
    for i,name in [(1,'R04_A5_Controls.png'),(2,'R04_Coordinated_Views.png'),(3,'R04_Section_and_Top.png')]:
        d[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(OUT/name)
    return path

def validate(data,path):
    checks=[]
    for name,d in data['parts'].items():
        v=np.array(d['vertices']);faces=d['faces_zero_based'];assert np.isfinite(v).all()
        assert all(0<=i<len(v) for face in faces for i in face)
        # Closed envelope: every undirected edge belongs to exactly two faces.
        edges={}
        for f in faces:
            for a,b in zip(f,f[1:]+f[:1]):
                k=tuple(sorted((a,b)));edges[k]=edges.get(k,0)+1
        assert all(n==2 for n in edges.values()),name
        checks.append(f'{name}: finite coordinates, valid indices, closed envelope')
    doc=pymupdf.open(path);assert len(doc)==8
    text='\n'.join(p.get_text() for p in doc)
    for s in ['13,601.7','12.7','2 coolers + 1 freezer','physical_scale_mm','unsized','16 October 2026']:
        assert s in text,s
    assert data['physical_scale_mm'] is None and data['host_plan_placement'] is None
    original=ROOT/'01_Source_Drawings_and_References/348 Front newst Drawing.pdf'
    assert hashlib.sha256(original.read_bytes()).hexdigest()=='48e949ee0bb6051d611d0eb6a0a462fb21bd0b3f5b06772c5fe904aa92eb99a8'
    report={'revision':'R04','date':DATE,'pdf_pages':len(doc),'component_checks':checks,
            'shared_projection_basis':'same serialized parameters and profiles as OBJ',
            'physical_fit_status':'NOT VALIDATED; unsized component only',
            'source_A5_sha256_unchanged':True,'visual_review':'Required after generation'}
    (OUT/'R04_Validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'pdf':str(path),'pages':len(doc),'size_bytes':path.stat().st_size,'mesh_parts':len(data['parts'])}))

def main():
    CAD.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True);font_setup()
    data=model();axon(data);path=pages(data);validate(data,path)

if __name__=='__main__':main()
