本次更新：仅修改 `paper/sec/4_evaluation_conditions.tex` 的正文文字；图表、caption、参考文献和supplementary源码与你上传的版本一致。正文占满8页，参考文献从第9页开始。

# GaitEval v2.2 LaTeX 编辑包

这是当前 GitHub 提交 15586dcef026a06a53035228d313564807447b32 的源码快照。正文当前8页，参考文献从第9页开始，共3页；正文6张表、两幅图，supplementary29页。红字审阅项保持，正文与补充材料均可编辑。

## 编辑入口

- `paper/main.tex`：正文入口；分节文字在 `paper/sec/`。
- `paper/supplementary_standalone.tex`：补充材料入口；内容在 `paper/supplementary.tex`。
- `paper/tables/`：独立表格源码；是否出现在正文由正文中的 input 控制。
- `paper/figures/`：已编译图、可编辑SVG和PNG；直接编辑文字排版无需重画图。
- `figure_source/`：绘图Python源码、素材、字体及许可说明；图源相对目录保留。
- `paper/main.bib` 与 `paper/references_frozen.bbl`：完整参考文献；当前稿通过冻结BBL保持67条参考文献内容及编号，常规文字排版修改无需运行BibTeX。
- `paper/main.pdf`、`paper/supplementary_standalone.pdf`：当前编译结果，供对照。
- `CHANGES_AND_OPEN_ISSUES_CN.md`：现有改动和待核实项。

## 本地编译

安装常规TeX Live或MiKTeX后，从包根目录执行 `bash BUILD.sh`。也可以在 `paper/` 目录先运行三次：

```bash
pdflatex -interaction=nonstopmode -halt-on-error supplementary_standalone.tex
```

再运行三次：

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

正文会读取补充材料AUX中的表号，因此先编译supplementary再编译main。包中附有当前版本的精简 `supplementary_standalone.aux`，便于首次直接编译正文；补充表编号发生变化后，按上述顺序重新编译即可。

## Overleaf

上传此ZIP作为新项目，选择 `paper/supplementary_standalone.tex` 为Main document并编译；随后切换为 `paper/main.tex` 并编译。若项目解压后外层还有 `GaitEval_v2.2_LaTeX/`，入口路径相应加上该文件夹。编译器选择pdfLaTeX。

## 重画图（可选）

包中不包含安装包。`figure_source/requirements.txt` 仅列出重画图所需的Python依赖；编译论文不需要安装这些Python依赖。图像来源说明见 `figure_source/ASSET_CREDITS.md`。
