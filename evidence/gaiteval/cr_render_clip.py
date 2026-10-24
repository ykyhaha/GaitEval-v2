#!/usr/bin/env python3
"""Camera-ready qualitative renderer: one clip, K keyframes, per-frame translation
removed (centered on the hip midpoint / valid-joint centroid) with ONE shared scale
across frames, so pose shape stays readable even when the subject walks across the
capture volume (Kinect meters / MediaPipe world coords)."""
import argparse, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skeleton_render import resolve_bones

ap = argparse.ArgumentParser()
ap.add_argument("--npz", required=True)
ap.add_argument("--index", type=int, required=True)
ap.add_argument("--joint-names", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--k", type=int, default=6)
ap.add_argument("--plane", default="xy", choices=["xy","xz"], help="projection plane; xz for z-up data (Kinect)")
a = ap.parse_args()

names = json.loads(a.joint_names)
arr = np.load(a.npz)
seq = arr["sequences"][a.index]  # (T,J,3)
if "lengths" in arr:
    T = int(arr["lengths"][a.index])
    seq = seq[:max(T, 2)]
bones = resolve_bones(names)
# complete Kinect-25 connectivity (spine chain + arms + hip attachment) missing
# from skeleton_render's alias list
_KINECT_EXTRA = [("spinebase","spinemid"),("spinemid","spineshoulder"),
    ("spineshoulder","neck"),("neck","head"),
    ("spineshoulder","shoulderleft"),("spineshoulder","shoulderright"),
    ("shoulderleft","elbowleft"),("elbowleft","wristleft"),
    ("shoulderright","elbowright"),("elbowright","wristright"),
    ("spinebase","hipleft"),("spinebase","hipright"),
    ("ankleleft","footleft"),("ankleright","footright")]
_lidx = {n.lower(): i for i, n in enumerate(names)}
for a2, b2 in _KINECT_EXTRA:
    if a2 in _lidx and b2 in _lidx and (_lidx[a2], _lidx[b2]) not in bones:
        bones.append((_lidx[a2], _lidx[b2]))
idx = {n.lower(): i for i, n in enumerate(names)}
head_i = next((idx[n] for n in ("nose", "head") if n in idx), None)
hipL = next((idx[n] for n in ("left_hip", "hipleft", "hip_left") if n in idx), None)
hipR = next((idx[n] for n in ("right_hip", "hipright", "hip_right") if n in idx), None)

PLANE = (0, 1) if a.plane == "xy" else (0, 2)
FLIP = -1.0 if a.plane == "xy" else 1.0   # image coords are y-down; z-up needs no flip

def valid(f):
    xy = f[:, list(PLANE)]
    return np.isfinite(xy).all(axis=1) & (np.abs(f).sum(axis=1) > 1e-9)

frames = np.linspace(0, seq.shape[0] - 1, a.k).astype(int)
centered = {}
for fi in frames:
    f = seq[fi].copy(); ok = valid(f)
    g = f[:, list(PLANE)].copy()
    if hipL is not None and hipR is not None and ok[hipL] and ok[hipR]:
        c = (g[hipL] + g[hipR]) / 2
    elif ok.any():
        c = g[ok].mean(axis=0)
    else:
        c = np.zeros(2)
    g -= c
    centered[fi] = (g, ok)

# one shared scale across keyframes (preserve amplitude differences)
span = 1e-3
for g, ok in centered.values():
    if ok.any():
        span = max(span, np.ptp(g[ok, 0]), np.ptp(g[ok, 1]))
m = 0.62 * span

fig, axes = plt.subplots(1, a.k, figsize=(2.2 * a.k, 3.6))
for ax, fi in zip(np.atleast_1d(axes), frames):
    g, ok = centered[fi]
    x, yy = g[:, 0], FLIP * g[:, 1]
    for b1, b2 in bones:
        if ok[b1] and ok[b2]:
            ax.plot([x[b1], x[b2]], [yy[b1], yy[b2]], "-", color="#1f4e79", lw=6,
                    solid_capstyle="round", zorder=2)
    ax.scatter(x[ok], yy[ok], s=36, color="#1f4e79", zorder=3)
    if head_i is not None and ok[head_i]:
        ax.add_patch(plt.Circle((x[head_i], yy[head_i]), 0.05 * span,
                                color="#1f4e79", zorder=3))
    ax.set_title(f"frame {fi}", fontsize=9)
    ax.set_xlim(-m, m); ax.set_ylim(-m, m)
    ax.set_aspect("equal"); ax.axis("off")
fig.suptitle("Keyframes left-to-right over time (per-frame centered)", fontsize=11)
fig.tight_layout()
fig.savefig(a.out, dpi=120, bbox_inches="tight", facecolor="white")
print("wrote", a.out, "T=", seq.shape[0], "J=", seq.shape[1])
