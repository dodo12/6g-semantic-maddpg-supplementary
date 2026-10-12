import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Environnement radio : garde-fous physiques."""
import sys, unittest
import numpy as np
# (portable : SUPP_ROOT/code, voir en-tete)
from src.radio_environment.channel import step_rate_bps, pathloss_db, doppler_hz


class TestRadio(unittest.TestCase):
    def test_rate_sanity(self):
        rng = np.random.default_rng(0)
        rates = [step_rate_bps(2.0, 250e6, 90.0, rng=rng)[0] for _ in range(20)]
        self.assertTrue(all(r > 0 for r in rates))
        se = np.mean(rates) / 250e6
        self.assertGreater(se, 0.05)
        self.assertLess(se, 30.0)  # garde-fou : SE aberrante = echec

    def test_distance_ordering(self):
        rng = np.random.default_rng(1)
        r_near = np.mean([step_rate_bps(2.0, 250e6, 60.0, rng=rng)[0] for _ in range(10)])
        r_far = np.mean([step_rate_bps(2.0, 250e6, 120.0, rng=rng)[0] for _ in range(10)])
        self.assertGreater(r_near, r_far)

    def test_doppler(self):
        self.assertAlmostEqual(doppler_hz(10.0), 259.3, delta=1.0)
        self.assertAlmostEqual(doppler_hz(30.0), 777.8, delta=3.0)  # 0.78 kHz = 30 km/h (ER19)


if __name__ == "__main__":
    unittest.main(verbosity=2)
