# pipeline/

Python scripts that take the raw CSV exports in `DATA_DIR/` (produced by the
scripts in `gee-full-script/`) and turn them into the cleaned tables in
`outputs/` and the figures in `figures/`.

Expected scripts (see docs/reproduce.html for usage):

- `01_clean_join.py` — parses the `LandUseDistribution` JSON column, joins
  benchmark-year land cover onto the per-buffer burn table.
- `02_fit_regressions.py` — fits the within-year, multi-year, and pooled OLS
  regressions of burned area against precipitation described in
  Methodology → Step 5.
- `03_make_figures.py` — renders the figures referenced on the Results page.
