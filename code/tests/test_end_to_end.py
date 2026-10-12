import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Bout-en-bout : identites physiques + coherence des CSV produits."""
import sys, unittest, os
import pandas as pd
# (portable : SUPP_ROOT/code, voir en-tete)
R = os.path.join(SUPP_ROOT, "results") + os.sep


class TestEndToEnd(unittest.TestCase):
    def test_latency_additivity(self):
        lat = pd.read_csv(R + "latency_breakdown.csv", index_col=0)
        for m, r in lat.iterrows():
            self.assertAlmostEqual(r.total_ms, r.denc_ms + r.dtx_ms + r.dq_ms + r.ddec_ms, places=6)

    def test_energy_additivity(self):
        en = pd.read_csv(R + "energy_breakdown.csv", index_col=0)
        for m, r in en.iterrows():
            self.assertAlmostEqual(r.total_mj, r.etx_mj + r.ecomp_mj, places=6)

    def test_tx_identity_spot(self):
        B, Ru = 3.84e6, 250e6  # charge type alpha=0.05 (pleine frame loot)
        self.assertAlmostEqual(B / Ru * 1000, 15.36, places=2)

    def test_no_17gbits_ms_claim(self):
        self.assertGreater(17.5e9 / 250e6 * 1000, 10.0)  # 70 000 ms >> qq ms (ER8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
