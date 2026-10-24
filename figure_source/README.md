# Figure source

Run `python figure_source/draw_figures.py` from the root of `v2.1/` (or invoke the script by its absolute path).

The script writes `paper/figures/overview.{pdf,svg,png}` and `methods.{pdf,svg,png}`. PDF contains embedded fonts; SVG retains editable text and vector shapes, with original raster resource images embedded. PNG is exported at 450 dpi. No generative image model was used for these exact scientific diagrams.

The style follows the user's six reference images: a white background, coloured rounded outlines, pastel subpanels, handwritten labels, small black-outlined icons, filmstrips and explicitly routed arrows. Comic Neue regular/bold are supplied under the included OFL license. Mathematical symbols use DejaVu/STIX fallback; dataset headers use DejaVu Sans Bold.

Resource cards reuse the credited existing source images; they do not introduce new dataset pictures or invented patient measurements. The methods filmstrip uses the recorded corrected-L GMFCS case already verified in `evidence/qualitative/`. Small range, asymmetry, stability and smoothness graphics illustrate mathematical operations. They are not measured trajectories or performance estimates. The 124-frame / 32-frame coordinate views and the ATAXIA-PATHOGAIT transfer remain explicitly scoped L probes; the shared suite is not depicted as running those probes for every dataset.

The six source image files are retained byte-for-byte in `assets/`; display crops only remove unused source-image borders or labels. Source reuse conditions are recorded in `ASSET_CREDITS.md`. A source's availability does not imply a blanket image redistribution permission.
