import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Pipeline de compression : fumee sur donnees synthetiques (rapide)."""
import sys, unittest
import numpy as np
# (portable : SUPP_ROOT/code, voir en-tete)
from src.semantic_transformer.encoder import AttentionScorer, BottleneckAE, compress_frame, baseline_uniform


class TestCompressionPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(0)
        cls.pts = rng.uniform(0, 1, (200, 6))
        cls.vox = cls.pts.copy()
        cls.vox[:, :3] *= 1023
        cls.vox[:, 3:] *= 255
        cls.ae = BottleneckAE(seed=0)
        cls.ae.mlp.max_iter = 50
        cls.ae.fit(cls.pts)
        cls.order = np.argsort(-AttentionScorer(seed=0).scores(cls.pts))

    def test_compress(self):
        m = compress_frame(self.pts, self.vox, 0.1, self.order, self.ae)
        self.assertGreater(m["stream_bytes"], 0)
        self.assertGreater(m["alpha_measured"], 0)
        self.assertLess(m["alpha_measured"], 1.0)
        self.assertTrue(np.isfinite(m["d1_psnr_db"]))
        self.assertGreaterEqual(m["enc_ms"], 0)

    def test_uniform(self):
        u = baseline_uniform(self.pts, self.vox, 0.1)
        self.assertGreater(u["d1_psnr_db"], 0)

    def test_alpha_ordering(self):
        a = compress_frame(self.pts, self.vox, 0.05, self.order, self.ae)
        b = compress_frame(self.pts, self.vox, 0.5, self.order, self.ae)
        self.assertLess(a["stream_bytes"], b["stream_bytes"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
