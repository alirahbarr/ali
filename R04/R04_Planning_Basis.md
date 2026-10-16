# R04 planning basis — source-based restaurant design development

16 October 2026 · 352 Front Street West, Unit 105 / customer entrance 348 Front Street West

**Owner decision:** the compact **R03 V02** image is approved as the visual direction for development. This selects its compact deep rounded-rectangular brick portal, broad piers, curved cashier, opaque backing and restrained palette. It does not approve dimensions, working access, site fit, accessible circulation, structural support, a product, a permit revision or fabrication.

**Available information:** the owner confirms that the supplied PDFs are the available drawings; no DWG or measured current sections are available. Continue source-based planning and consistent component studies now. Do not repeatedly request the same unavailable DWG or postpone independent design development because it is absent.

A5 remains the owner-confirmed latest working plan, dated 2026/JUN/19. City acceptance and field accuracy remain unverified. Historical architecture is supporting evidence only. Preserve R01–R03 decisions, including removed ground-floor tiles, confirmed LEFT refrigeration wall, takeout-led operation, approximately 5–6 downstairs seats, retained current ground universal WC and separate conditional future WC/storage scenario.

## Immediate design constraints

1. **Public plan first:** preserve a separate guest-right approach to the stair. A5 does not demonstrate an independent public connection from that side to the rear/guest-left universal WC. Keep that conflict visible; do not draw a continuous green public route through the kitchen, equipment bank or an invented rear passage.
2. **Enclosed kitchen:** the compact portal frames a cashier composition with opaque backing. It is not a public kitchen passage or an open-kitchen serving window. Staff entry, pickup and service access still need deliberate positions.
3. **Refrigeration:** confirmed LEFT when entering = sheet TOP on landscape A5. Preserve **two two-door coolers plus one two-door freezer**. The intended wall is answered; exact positions, operating/ventilation/removal envelopes and current-versus-future timing remain open. Do not allocate the retained WC as available refrigeration/storage area.
4. **Forward projection:** the kitchen/brick volume is intended to extend toward the entrance beyond the white TV-fascia area. That visible fascia is not a verified mezzanine structural datum. The projection must remain an adjustable design variable until those references are matched, rather than being silently fixed to the source mezzanine line.
5. **Three assemblies:** existing mezzanine structure, kitchen enclosure/ceiling and decorative portal support remain separately coordinated. Finish the upper surface for the mezzanine view without creating a walking/storage platform. No withdrawn curved upper-mezzanine ceiling-edge work is reintroduced.
6. **Cashier operation:** substantial piers/deep returns can reduce the front arrival zone, staff entry and useful view. Approximately120-degree visibility is a target, not proven by V02. The front area must accommodate takeout queue/pickup and any retained seats as well as the independent guest route.

## Yes: the A5 vector source can become a reliable reference underlay

Direct PDF inspection finds **7,479 vector drawing paths and no embedded raster images**. A clean vector SVG can preserve the supplied drawing faithfully, including curves, labels and linework. Geometry can also be transferred to a DXF reference layer. This is a reproducible extraction of source ink, **not a new survey, a confirmed as-built plan, or semantic identification of every wall**.

A5 has native media/crop size **792 x1224 PDF points**, with **/Rotate270**. Its correctly displayed landscape page is **1224 x792 points**. For primitive geometry returned in native coordinates by PyMuPDF `get_drawings`, apply the page rotation once:

`x_display = y_native`  
`y_display = 792 - x_native`

PyMuPDF `get_svg_image(text_as_path=True)` already exports a **1224 x792 displayed landscape SVG**. Do not rotate that SVG again. Verify entrance-left, rear-right and title-block orientation after every embedding/export, as double rotation creates a plausible-looking but wrong underlay.

The printed scale **3/16 inch =1 foot** corresponds to **1:64** or **22.5777778 mm per displayed PDF point**. Use a uniform nominal conversion. Choose a reproducible control origin at display point **(445.32,212.46)**, the intersection of the storefront longitudinal witness and guest-left transverse datum. This is a reference-axis intersection, not a surveyed corner. For study coordinates:

`X_mm = (x_display -445.32) x22.5777778`  
`Y_mm = (y_display -212.46) x22.5777778`

X increases from storefront toward rear. In an SVG/image, Y increases from guest-left toward guest-right. If CAD uses Y-up, use `Y_CAD = -Y_mm` and record that sign convention. The companion **R04_A5_Control_Anchors.json** provides 17 extracted controls, source hash, mapping, trace residuals and evidence status. Its decimal precision supports reproducibility; it does not imply millimetre site accuracy.

### Keep ink geometry and written dimensions separate

| Control span | Written source value | Uniform nominal vector trace | Difference: trace minus written |
|---|---:|---:|---:|
| Overall longitudinal | 13,601.7 mm | 13,596.8 mm | -4.9 mm |
| Front transverse | 6,159.5 mm | 6,165.1 mm | +5.6 mm |
| Rear transverse | 5,448.3 mm | 5,449.8 mm | +1.5 mm |
| Front split to wall jog | 6,121.4 mm | 6,123.1 mm | +1.7 mm |
| Rear split from wall jog | 7,467.6 mm | 7,473.7 mm | +6.1 mm |
| Storefront to rectangular P.O.S leading face | 2,806.7 mm | 2,812.3 mm | +5.6 mm |

The source P.O.S leading face is at display **X569.88 pt**, the mezzanine limit at **X792.18 pt** and the storefront witness at **X445.32 pt**. The nominal trace interval from P.O.S face to source mezzanine limit is **5,019.0 mm**. This is a source-control interval only: it is **not** the proposed kitchen-roof projection, an available staff/cashier depth, a structural span or proof of fit.

These small plotted-geometry residuals do not resolve the **separate written-chain discrepancy**: 20 ft1 in +24 ft6 in =44 ft7 in, versus the written overall 44 ft7½ in, a **12.7 mm difference**. Keep both types of inconsistency recorded. Do not use different X/Y scaling, stretch the source outline, snap wall faces to conflicting labels, distribute discrepancies, or average source and historical dimensions to make a closed plan.

### Safe extraction method

- Preserve the unmodified full A5 as the document-of-record underlay. Export its full displayed SVG with vector text outlines for visual fidelity; retain an editable source-dimension schedule separately.
- For a working plan viewport, clip a **copy** of the displayed source; leave the full sheet accessible. A crop is a plotting choice, not the restaurant boundary. Include storefront leaf/swing, columns, walls, jog, stair, retained WC, electrical equipment and FHC; inspect that nothing needed for access/fit is accidentally clipped.
- Map the copied source ink uniformly into millimetres on **SOURCE_INK_REFERENCE**. Preserve source curves as curves where supported. An intentional curve tessellation must state tolerance; do not fit new arcs or straighten bends without recording the approximation.
- A5 linework is not a complete labelled CAD model: counters, equipment, dimension circles, hatches and walls must not all be auto-classified as walls. Use a neutral source-ink layer first, then add individually identified controls or components with source provenance.
- In DXF, retain correct units and the documented Y convention; label source ink **REFERENCE TRACE—NOT SURVEY—DO NOT USE FOR CONSTRUCTION SET-OUT**. Do not manufacture wall thickness, room objects or structural properties from line weights. A companion PDF/SVG supplies labels if source font mapping is incomplete.
- Perform a round-trip render and compare the front/rear witnesses, wall jog, P.O.S rectangle, mezzanine limit, door swing, stair and WC. Verify at least two independent controls in each axis; the comparison is to the source, not a declaration that the source matches the building.

## Four evidence classes on every R04 sheet

| Class | Display / data policy | Example |
|---|---|---|
| **Written source dimension** | Cite A5/source ID; use the exact written value; label NOT FIELD VERIFIED | 44 ft7½ in overall; 9 ft2½ in source P.O.S reference |
| **Source-traced control** | Neutral reference colour/linetype; record nominal mapping; never label surveyed/existing verified | Mezzanine dashed limit at display X792.18; source wall-jog faces |
| **Proposed adjustable design parameter** | Distinct proposal colour; named and revision-controlled; trial value or UNSIZED; never presented as an existing measurement | New enclosure-front position, portal width/depth, counter bow, staff recess, screen offset |
| **Unknown site/vertical information** | Mark NOT SUPPLIED / TO VERIFY; do not populate a physical 3D host value from a photograph | Actual floor levels, beam/soffit height, TV-fascia relationship, portal support zone, mezzanine sightline |

A proposed trial dimension is a design choice and may be developed transparently for comparison; it is not a fabricated source measurement. Keep `proposed_trial_mm` separate from `source_written_mm`, `source_trace_mm` and `field_verified_mm`. Do not assign false floor/ceiling heights or select a final radius/counter size merely to make a render look complete.

## Concrete R04 sheet set

| Sheet | Work to produce now | Test / limit |
|---|---|---|
| **R04-01 Source and control plan** | Correctly oriented, unaltered A5 underlay; millimetre reference trace; numbered controls; independent written dimension axes and discrepancy note | Establish one reproducible source basis; retain the WC and original equipment identities |
| **R04-02 Ground-floor planning constraints** | Source-based plan with separate kitchen/public/service zones, retained WC, guest-right stair approach and a prominent unresolved public-WC connection; front takeout queue/pickup and 5–6-seat target recorded | Show where tests are needed; do not fill the unresolved link with an invented compliant route or confirmed seat layout |
| **R04-03 Cashier/portal local plan and front elevation** | Both generated from the same normalized V02-derived component geometry; identify curved counter, piers, deep soffit, opaque screen, staff recess/entry and transaction interface as design parameters | Compact appearance can advance now. Put normalized geometry in its own UNSIZED detail viewport; do not superimpose an unsized object on the source plan as though it has a physical footprint |
| **R04-04 Longitudinal relationship study** | Front-to-rear source control strip, source floor-limit reference, adjustable kitchen projection and independently represented enclosure/ceiling/portal; schematic Z-axis with all site heights unknown | Do not equate TV fascia and structural edge or use the source ground-floor PDF to invent a measured section |
| **R04-05 Top view / mezzanine-facing study** | Same component's finished cap/top, back of screen, joins, services/access zones and relationship to the mezzanine viewing direction | Use a diagrammatic eye/view arrow. Actual eye level, guard/edge geometry and visibility remain unverified; no certified sightline |
| **R04-06 Scenario and decision sheet** | Current retained-WC baseline, refrigeration option along confirmed guest-left wall, and separate unapproved storage/added-upstairs-WC scenario | Keep phase undecided for refrigeration; do not make that move automatically depend on WC conversion or release WC floor area |

The normalized component's local plan, elevation, longitudinal view and view from above must share one shape definition. An approved image is a form reference, not an existing CAD model: do not scale it by assumed brick courses, counter height, people, perspective or room width. Record any dimensionless proportions as **proposed study geometry**. Use a single reference width of 1 normalized unit; physical width, height, depth and radius stay independently named adjustable variables, not assumed site dimensions.

## Coordinated fit strategy

1. **Lock the source, not a guessed building.** Keep source ink read-only and independently transcribed dimensions unchanged. Identify the storefront, columns, wall jog, source P.O.S rectangle, stair, WC, FHC and electrical-panel conditions before selecting a proposed envelope.
2. **Use the P.O.S rectangle as a starting location reference only.** The owner wishes to keep the cashier near the hallway entrance; A5's rectangular footprint does not establish the new curved counter or arch. The owner 9–10 ft estimate is an approximate brief reference, not an enclosure-front set-out.
3. **Test the public/service plan together.** A front arrangement must reserve independent guest-right travel, takeout waiting/collection, the intended public transaction and staff access. Keep the public-WC conflict explicit until a complete route is shown around the kitchen; do not hide it behind a material volume.
4. **Parameterize the kitchen front.** The proposed front position and full build-up of counter, staff recess, opaque screen, piers and enclosure consume real space. Test those together rather than adding a deep arch after the operational plan is fixed. Retain service/cleaning access and check projections against columns and cabinets.
5. **Test refrigeration by actual function.** C1/C2/F1 remain cooler/cooler/freezer, along the owner-confirmed left wall. Until models are selected, show source footprints as reference and proposed manufacturer envelopes as pending; do not certify door clearances or flush placement.
6. **Fit seats after route/operations.** Test approximately 5–6 downstairs seats as an adjustable target. Mezzanine dining/table aspirations require a separate current footprint/vertical/stair study; historical seat counts are not a current capacity approval.
7. **Keep future changes independent.** The current ground universal WC is retained. Upstairs WC condition and a possible second fixture are unverified. A storage scenario is separately conditional; it supplies no current room area or cost saving.

## Controls needed for the next physically exact layout

Independent work can proceed using this source trace and unsized component now. The next exact issue requires a targeted site measurement record, rather than another request for an unavailable drawing:

- Match the source storefront and rear witnesses, both side-wall runs, wall jog, columns and diagonals; record finished faces and discrepancies.
- Measure the front arrival/P.O.S/corridor zone; locate actual door clear opening/swing, counter staff access, FHC/panel access and queue/pickup interfaces.
- Locate the ground WC's door and fixtures, its clear finished boundaries and possible public approach; record upstairs W/C conditions separately.
- Match actual mezzanine edge/beam/TV-fascia faces; measure ground-to-mezzanine/soffit/lowest services, mezzanine-to-lowest obstruction, stairs, landings and guards.
- Identify equipment models and open-door/service envelopes; locate gas/power/drainage/exhaust/makeup routes and maintenance needs.

This R04 basis advances an actual coordinated design study without presenting a conceptual portal as a fabricated site measurement. Final arch/counter sizes, accessible circulation, WC solution, loading/support and construction approval remain outside what the present evidence establishes.
