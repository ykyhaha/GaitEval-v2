# GaitEval v2.1 — master results (Phase 1-4)

Point metrics: runner fixed-K macro-F1. CI: 95% subject-cluster bootstrap (UNPARSED-sentinel convention). p: permutation vs stratified chance.

## Per-cell

| dataset | condition | n | mF1 | 95% CI | perm p | unparsed |
|---|---|---|---|---|---|---|
| ataxia | ref LR (feat) | 8 | 0.873 | [0.5636, 1.0] | 0.0645 | – |
| ataxia | ref chance | 8 | 0.4881 | – | – | – |
| ataxia | 7B zs | 8 | 0.2727 | [0.1111, 0.3333] | 1.0 | 0 |
| ataxia | 7B feat | 8 | 0.3333 | [0.3333, 0.3333] | 1.0 | 0 |
| ataxia | 7B sft | 8 | 0.3333 | [0.3333, 0.3333] | 1.0 | 0 |
| ataxia | 7B lorder-rev | 8 | 0.2727 | [0.1111, 0.3333] | 1.0 | 0 |
| ataxia | 7B lorder-shuf1 | 8 | 0.2727 | [0.1111, 0.3333] | 1.0 | 0 |
| ataxia | 7B shufev | 8 | 0.2727 | [0.1111, 0.3333] | 1.0 | 0 |
| ataxia | 7B noev | 8 | 0.3333 | [0.3333, 0.3333] | 1.0 | 0 |
| gmfcs | ref LR (feat) | 255 | 0.5788 | [0.4736, 0.6623] | 0.0005 | – |
| gmfcs | ref chance | 255 | 0.2501 | – | – | – |
| gmfcs | 7B zs | 255 | 0.2647 | [0.2171, 0.3081] | 0.0415 | 0 |
| gmfcs | 7B feat | 255 | 0.1501 | [0.1084, 0.1973] | 0.4158 | 0 |
| gmfcs | 7B sft | 255 | 0.467 | [0.4132, 0.624] | 0.0005 | 0 |
| gmfcs | 7B lorder-rev | 255 | 0.3215 | [0.2712, 0.3694] | 0.006 | 0 |
| gmfcs | 7B lorder-shuf1 | 255 | 0.2742 | [0.2251, 0.3197] | 0.1319 | 0 |
| gmfcs | 7B shufev | 255 | 0.2124 | [0.1722, 0.2519] | 0.6237 | 0 |
| gmfcs | 7B noev | 255 | 0.0 | [0.0, 0.0] | 1.0 | 255 |
| parkinsonism | ref LR (feat) | 29 | 0.5606 | [0.4156, 0.6538] | 0.2384 | – |
| parkinsonism | ref chance | 29 | 0.4941 | – | – | – |
| parkinsonism | 7B zs | 29 | 0.3958 | [0.2222, 0.5297] | 0.5237 | 0 |
| parkinsonism | 7B feat | 29 | 0.7575 | [0.5429, 0.906] | 0.0075 | 0 |
| parkinsonism | 7B sft | 29 | 0.5421 | [0.2552, 0.72] | 0.2929 | 0 |
| parkinsonism | 7B lorder-rev | 29 | 0.3556 | [0.1364, 0.6167] | 0.8956 | 0 |
| parkinsonism | 7B lorder-shuf1 | 29 | 0.3556 | [0.1364, 0.6167] | 0.8956 | 0 |
| parkinsonism | 7B shufev | 29 | 0.3095 | [0.1038, 0.439] | 1.0 | 0 |
| parkinsonism | 7B noev | 29 | 0.3256 | [0.1333, 0.4615] | 1.0 | 0 |
| pathogait | ref LR (feat) | 1440 | 0.8809 | [0.8809, 0.8809] | 0.0005 | – |
| pathogait | ref chance | 1440 | 0.1664 | – | – | – |
| pathogait | 7B zs | 1440 | 0.069 | [0.069, 0.069] | 0.6227 | 0 |
| pathogait | 7B feat | 1440 | 0.1387 | [0.1189, 0.1189] | 0.0005 | 1 |
| pathogait | 7B sft | 1440 | 0.451 | [0.451, 0.451] | 0.0005 | 0 |
| pathogait | 7B lorder-rev | 1440 | 0.1207 | [0.1207, 0.1207] | 0.0005 | 0 |
| pathogait | 7B lorder-shuf1 | 1440 | 0.0934 | [0.0934, 0.0934] | 0.1719 | 0 |
| pathogait | 7B shufev | 1440 | 0.0706 | [0.0706, 0.0706] | 0.4798 | 0 |
| pathogait | 7B noev | 1440 | 0.0476 | [0.0476, 0.0476] | 1.0 | 0 |
| asd_kinect | ref LR (feat) | 20 | 0.697 | [0.4792, 0.8903] | 0.09 | – |
| asd_kinect | ref chance | 20 | 0.4905 | – | – | – |
| asd_kinect | 7B zs | 20 | 0.3103 | [0.2, 0.3939] | 1.0 | 0 |
| asd_kinect | 7B feat | 20 | 0.4357 | [0.2593, 0.6416] | 0.4983 | 0 |
| asd_kinect | 7B sft | 20 | 0.3103 | [0.2, 0.3944] | 1.0 | 0 |
| asd_kinect | 7B lorder-rev | 20 | 0.3407 | [0.1667, 0.5238] | 0.9585 | 0 |
| asd_kinect | 7B lorder-shuf1 | 20 | 0.3407 | [0.1667, 0.5238] | 0.9585 | 0 |
| asd_kinect | 7B shufev | 20 | 0.4357 | [0.2593, 0.6416] | 0.5137 | 0 |
| asd_kinect | 7B noev | 20 | 0.3333 | [0.2308, 0.4122] | 1.0 | 0 |
| care_pd | ref LR (feat) | 970 | 0.4636 | [0.3233, 0.5422] | 0.0005 | – |
| care_pd | ref chance | 970 | 0.0832 | – | – | – |
| care_pd | 7B zs | 665 | 0.3206 | [0.2619, 0.4041] | 0.0005 | 0 |
| care_pd | 7B feat | 665 | 0.1335 | [0.0856, 0.1844] | 0.6772 | 0 |
| care_pd | 7B sft | 665 | 0.4446 | [0.2597, 0.5075] | 0.0005 | 0 |
| care_pd | 7B lorder-rev | 665 | 0.2523 | [0.1332, 0.2927] | 0.0005 | 0 |
| care_pd | 7B lorder-shuf1 | 665 | 0.2849 | [0.217, 0.3529] | 0.0005 | 0 |
| care_pd | 7B shufev | 665 | 0.256 | [0.2166, 0.3126] | 0.2299 | 0 |
| care_pd | 7B noev | 665 | 0.1326 | [0.0832, 0.1826] | 1.0 | 0 |
| care_pd | 7B zs_mixed | 970 | 0.0036 | [0.0006, 0.0088] | 1.0 | 0 |

### Caveats

- **pathogait**: the v2.1 test split has 2 subjects (720 clips each); subject-cluster bootstrap is degenerate (CIs collapse to a point) and row-level permutation p is anti-conservative under clustering. Treat pathogait LLM cells as sample-level point estimates; subject-level uncertainty comes from the Phase-1 LOSO reference (12 subjects).
- **ataxia**: n=8 test clips over 3 subjects; no power (perm p=1.0 even at mF1 .27). LOSO reference (20 subjects) is the primary number.
- **asd_kinect**: 1 clip per subject; cluster bootstrap reduces to an ordinary bootstrap.
- **care_pd zs_mixed** (12-class mixed-label variant) is a diagnostic cell, not a benchmark number.

## Paired contrasts (subject-paired bootstrap, macro-F1)

| dataset | contrast | delta | 95% CI | p |
|---|---|---|---|---|
| asd_kinect | zs − noev | -0.023 | [-0.0796, 0.0] | 0.7026 |
| asd_kinect | zs − shufev | -0.1254 | [-0.3096, 0.0] | 0.2469 |
| asd_kinect | zs − feat | -0.1254 | [-0.3164, 0.0] | 0.2449 |
| asd_kinect | zs − lorder-rev | -0.0303 | [-0.2063, 0.1111] | 0.8916 |
| asd_kinect | zs − lorder-shuf1 | -0.0303 | [-0.2063, 0.1111] | 0.8916 |
| asd_kinect | sft − zs | 0.0 | [-0.1939, 0.2118] | 1.0 |
| ataxia | zs − noev | -0.0606 | [-0.2222, 0.0] | 0.6009 |
| ataxia | zs − shufev | 0.0 | [-0.2222, 0.2222] | 1.0 |
| ataxia | zs − feat | -0.0606 | [-0.2222, 0.0] | 0.6009 |
| ataxia | zs − lorder-rev | 0.0 | [0.0, 0.0] | 1.0 |
| ataxia | zs − lorder-shuf1 | 0.0 | [0.0, 0.0] | 1.0 |
| ataxia | sft − zs | 0.0606 | [0.0, 0.2222] | 0.6009 |
| care_pd | zs − noev | 0.188 | [0.101, 0.2618] | 0.001 |
| care_pd | zs − shufev | 0.0646 | [0.0069, 0.1175] | 0.029 |
| care_pd | zs − feat | 0.1872 | [0.0972, 0.2842] | 0.002 |
| care_pd | zs − lorder-rev | 0.0683 | [0.0057, 0.2095] | 0.028 |
| care_pd | zs − lorder-shuf1 | 0.0357 | [0.0011, 0.0844] | 0.045 |
| care_pd | sft − zs | 0.1239 | [-0.0521, 0.1894] | 0.4288 |
| gmfcs | zs − noev | 0.2647 | [0.2171, 0.3081] | 0.001 |
| gmfcs | zs − shufev | 0.0523 | [-0.0076, 0.1085] | 0.089 |
| gmfcs | zs − feat | 0.1146 | [0.0492, 0.1704] | 0.004 |
| gmfcs | zs − lorder-rev | -0.0568 | [-0.1102, -0.0072] | 0.03 |
| gmfcs | zs − lorder-shuf1 | -0.0095 | [-0.0383, 0.0193] | 0.5237 |
| gmfcs | sft − zs | 0.2022 | [0.136, 0.3513] | 0.001 |
| parkinsonism | zs − noev | 0.0703 | [0.0, 0.1256] | 0.6246 |
| parkinsonism | zs − shufev | 0.0863 | [0.0, 0.1587] | 0.1447 |
| parkinsonism | zs − feat | -0.3616 | [-0.5635, -0.1143] | 0.001 |
| parkinsonism | zs − lorder-rev | 0.0403 | [-0.1986, 0.1587] | 0.6225 |
| parkinsonism | zs − lorder-shuf1 | 0.0403 | [-0.1986, 0.1587] | 0.6225 |
| parkinsonism | sft − zs | 0.1463 | [-0.2378, 0.4436] | 0.4748 |
| pathogait | zs − noev | 0.0214 | [0.0214, 0.0214] | 0.0019 |
| pathogait | zs − shufev | -0.0016 | [-0.0016, -0.0016] | 0.0019 |
| pathogait | zs − feat | -0.0499 | [-0.0499, -0.0499] | 0.0019 |
| pathogait | zs − lorder-rev | -0.0517 | [-0.0517, -0.0517] | 0.0019 |
| pathogait | zs − lorder-shuf1 | -0.0244 | [-0.0244, -0.0244] | 0.0019 |
| pathogait | sft − zs | 0.382 | [0.382, 0.382] | 0.0019 |
