"""Chargement 8iVFB : sous-echantillonnage uniforme + normalisation."""
import os
import numpy as np
import pandas as pd

RAW_DATA_DIR = os.environ.get("EIGHTIVFB_DATA", r"C:\8ivfb_audit\data")  # PLY d'origine (non redistribues)
AUDIT_DATA = RAW_DATA_DIR
FRAMES = {
 "loot_1000": ("loot", 1000), "loot_1150": ("loot", 1150), "loot_1299": ("loot", 1299),
 "longdress_1051": ("longdress", 1051), "longdress_1201": ("longdress", 1201),
 "longdress_1350": ("longdress", 1350),
 "redandblack_1450": ("redandblack", 1450), "redandblack_1600": ("redandblack", 1600),
 "redandblack_1749": ("redandblack", 1749),
 "soldier_536": ("soldier", 536), "soldier_686": ("soldier", 686),
 "soldier_835": ("soldier", 835),
}

def load_subsample(frame_id, ns=2048, seed=42):
    seq, fid = FRAMES[frame_id]
    path = os.path.join(AUDIT_DATA, f"{seq}_{fid}.ply")
    with open(path, "rb") as f:
        hlen = 0
        for i, line in enumerate(f):
            if line.strip() == b"end_header":
                hlen = i + 1
                break
    df = pd.read_csv(path, sep=" ", header=None, skiprows=hlen,
                     names=["x", "y", "z", "r", "g", "b"])
    rng = np.random.default_rng(seed + abs(hash(frame_id)) % 10000)
    idx = rng.choice(len(df), size=min(ns, len(df)), replace=False)
    pts = df.to_numpy()[np.sort(idx)].astype(np.float64)
    vox = pts.copy()
    pts[:, :3] /= 1023.0
    pts[:, 3:] /= 255.0
    return pts.astype(np.float32), vox  # normalise, voxel-brut (pour D1-PSNR)
