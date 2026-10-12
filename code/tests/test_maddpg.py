import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""MADDPG numpy : fumee (formes, buffer, mises a jour finies)."""
import sys, unittest
import numpy as np
# (portable : SUPP_ROOT/code, voir en-tete)
from src.maddpg.maddpg import MADDPG


class TestMADDPG(unittest.TestCase):
    def test_act_shapes(self):
        ag = MADDPG(n_agents=4, seed=0, buffer=200, batch=32)
        u = ag.act(np.zeros((4, 5)), noise=0.1)
        self.assertEqual(u.shape, (4, 3))
        p, shares, alpha = ag.map_actions(u)
        self.assertEqual(p.shape, (4,))
        self.assertAlmostEqual(float(shares.sum()), 1.0, places=6)
        self.assertTrue(bool(((alpha >= 0.02) & (alpha <= 0.5)).all()))
        self.assertTrue(bool(((p >= 0.1) & (p <= 2.0)).all()))

    def test_update_finite(self):
        ag = MADDPG(n_agents=2, seed=1, buffer=200, batch=32)
        rng = np.random.default_rng(0)
        for _ in range(40):
            o = rng.normal(size=(2, 5))
            ag.store(o, np.tanh(rng.normal(size=(2, 3))), 1.0, o)
        loss = ag.update()
        self.assertTrue(np.isfinite(loss))

    def test_shared_actor(self):
        ag = MADDPG(n_agents=4, seed=2, buffer=200, batch=32, shared_actor=True)
        u = ag.act(np.zeros((4, 5)))
        self.assertEqual(u.shape, (4, 3))
        ag.store(np.zeros((4, 5)), u, 0.5, np.zeros((4, 5)))
        self.assertEqual(len(ag.buf), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
