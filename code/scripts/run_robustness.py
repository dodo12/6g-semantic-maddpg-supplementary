import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Phase G (robustesse) : balayages SANS reapprentissage (methodes figees).
Conditions : B_total x{0.5,1,2} GHz ; lambda x{10,30} fps ; distances x{0.7,1.3}."""
import sys
import numpy as np
import pandas as pd
# (portable : SUPP_ROOT/code, voir en-tete)
sys.path.insert(0, os.path.join(SUPP_ROOT, "scripts"))
import importlib.util
spec = importlib.util.spec_from_file_location("phD", os.path.join(SUPP_ROOT, "scripts", "run_phaseD.py"))
phD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phD)

curves = phD.load_curves()
rng = np.random.default_rng(42)
conds = []
for B in (0.5e9, 1e9, 2e9):
    conds.append((f"B={B/1e9}GHz", dict(B_tot=B)))
for lam in (10.0, 30.0):
    conds.append((f"lam={lam}fps", dict(lam=lam)))
for ds in (0.7, 1.3):
    conds.append((f"dist x{ds}", dict(dist_scale=ds)))

rows = []
for name, kw in conds:
    for m in ("heuristic", "fixed1", "fixed05", "random"):
        qs, ls, vs = [], [], []
        for ep in range(20):
            r = phD.run_episode({"kind": m}, curves, rng, train=False, **kw)
            qs.append(r["qoe"]); ls.append(r["lat"]); vs.append(r["viol"])
        rows.append({"condition": name, "method": m, "qoe": float(np.mean(qs)),
                     "lat_ms": float(np.mean(ls)), "viol_rate": float(np.mean(vs))})
        print(name, m, round(float(np.mean(qs)), 3), round(float(np.mean(ls)), 1))
pd.DataFrame(rows).to_csv(os.path.join(SUPP_ROOT, "results", "robustness_results.csv"), index=False)
print("OK robustness", len(rows))
