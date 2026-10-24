from pathlib import Path
import runpy
R=Path(__file__).resolve().parents[1]
runpy.run_path(str(R/'figure_source/draw_figures.py'),run_name='__main__')
