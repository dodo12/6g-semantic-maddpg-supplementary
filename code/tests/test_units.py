import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Tests unitaires : physique (Doppler, T_tx, energie), QoE, MHA, flux code.
Echec exige en cas d'incoherence physique majeure."""
import os, sys, unittest
import numpy as np
# (portable : SUPP_ROOT/code, voir en-tete)
from src.radio_environment.channel import doppler_hz, queue_md1_ms
from src.metrics.qoe import qoe, qoe_raw, manuscript_bound_check
from src.semantic_transformer.encoder import AttentionScorer, pack_stream


class TestPhysics(unittest.TestCase):
    def test_doppler_10kmh_28ghz(self):
        # f_d = v*fc/c = 2.778*28e9/3e8 ~= 259 Hz (ER19 ; manuscrit 0.78 kHz FAUX)
        self.assertAlmostEqual(doppler_hz(10.0, 28e9), 259.3, delta=1.0)

    def test_t_tx_identity(self):
        B, R = 17.5e9, 250e6
        self.assertAlmostEqual(B / R, 70.0)  # 70 s, pas 3.5 ms (ER8)
        self.assertGreater(B / R * 1000, 10.0)

    def test_energy_units(self):
        self.assertAlmostEqual(2.0 * 367.2, 734.4)  # W*ms = mJ (Table V : Pmax constant)

    def test_queue_md1(self):
        d, rho = queue_md1_ms(30.0, 300.0)
        self.assertLess(d, 5.0)
        d2, rho2 = queue_md1_ms(30.0, 20.0)
        self.assertEqual(d2, 1000.0)  # saturation plafonnee documentee


class TestQoE(unittest.TestCase):
    def test_bounds(self):
        for q, d, e in [(90, 0, 0), (40, 50, 100), (67, 10, 20), (46, 3000, 5000)]:
            v = qoe(q, d, e)
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)

    def test_monotonic(self):
        self.assertGreater(qoe(90, 5, 5), qoe(50, 5, 5))   # qualite +
        self.assertGreater(qoe(70, 5, 5), qoe(70, 40, 5))   # delai -
        self.assertGreater(qoe(70, 5, 5), qoe(70, 5, 80))   # energie -

    def test_manuscript_claim_false(self):
        chk = manuscript_bound_check()
        self.assertFalse(chk["claim_valid"])
        self.assertAlmostEqual(chk["min_possible"], -0.4)
        self.assertAlmostEqual(chk["max_possible"], 0.6)


class TestEncoder(unittest.TestCase):
    def test_scorer_deterministic(self):
        rng = np.random.default_rng(0)
        x = rng.normal(size=(64, 6)).astype(np.float64)
        s1 = AttentionScorer(seed=7).scores(x)
        s2 = AttentionScorer(seed=7).scores(x)
        self.assertEqual(len(s1), 64)
        np.testing.assert_allclose(s1, s2)
        self.assertAlmostEqual(float(s1.sum()), 1.0, places=5)

    def test_stream_roundtrip_size(self):
        z = np.zeros((41, 16), dtype=np.float16)
        b = pack_stream(z, {"ns": 2048, "k": 41})
        import json
        hlen = int.from_bytes(b[:4], "little")
        meta = json.loads(b[4:4 + hlen].decode())
        self.assertEqual(meta["k"], 41)
        self.assertEqual(len(b), 4 + hlen + 41 * 16 * 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
