import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""QoE : bornes, monotonie, ecretage de la sensibilite."""
import sys, unittest
# (portable : SUPP_ROOT/code, voir en-tete)
from src.metrics.qoe import qoe


class TestQoEFile(unittest.TestCase):
    def test_clip_extreme_weights(self):
        self.assertLessEqual(qoe(90, 0, 0, w=(0.8, 0.1, 0.1)), 1.0)
        self.assertGreaterEqual(qoe(40, 50, 100, w=(0.4, 0.4, 0.2)), 0.0)

    def test_reference_weights(self):
        v = qoe(83.6, 10.0, 20.0)  # point de fonctionnement type (attn-select)
        self.assertGreater(v, 0.5)
        self.assertLessEqual(v, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
