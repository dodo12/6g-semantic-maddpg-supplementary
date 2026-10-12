import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Phase B : construit data/processed/subsampled.npz + results/data_split_manifest.csv."""
import os, sys, csv
import numpy as np
# (portable : SUPP_ROOT/code, voir en-tete)
from src.dataset.loader import load_subsample, FRAMES

TRAIN = ["loot_1000","loot_1150","longdress_1051","longdress_1201","redandblack_1450","redandblack_1600"]
VAL = ["loot_1299","longdress_1350","redandblack_1749"]
TEST = ["soldier_536","soldier_686","soldier_835"]

out = {}
manifest = []
for fid in list(FRAMES):
    pts, vox = load_subsample(fid, ns=2048, seed=42)
    out[fid] = pts
    out[fid + "_vox"] = vox
    split = "train" if fid in TRAIN else ("val" if fid in VAL else "test")
    role = {"train": "apprentissage", "val": "sélection hyperparamètres (frames futures)",
            "test": "test final (séquence soldier tenue à l'écart)"}[split]
    manifest.append({"frame": fid, "sequence": FRAMES[fid][0], "frame_id": FRAMES[fid][1],
                     "split": split, "role": role, "n_points_subsample": len(pts),
                     "seed": 42, "preprocessing": "uniforme Ns=2048, coords/1023, RGB/255"})
np.savez_compressed(os.path.join(SUPP_ROOT, "data", "processed", "subsampled.npz"), **out)
with open(os.path.join(SUPP_ROOT, "results", "data_split_manifest.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
    w.writeheader(); w.writerows(manifest)
print("OK", len(manifest), "frames;", {s: sum(1 for m in manifest if m['split']==s) for s in ('train','val','test')})
