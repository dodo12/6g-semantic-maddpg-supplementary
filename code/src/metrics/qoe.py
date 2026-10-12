"""QoE CORRIGEE. Manuscrit eq.11 : QoE = 0.6Q-0.25D-0.15E 'dans [0,1]' : FAUX
(min -0.4, max 0.6). Correction : QoE_c = (QoE_raw + 0.4)/1.0 dans [0,1].
Plages de normalisation explicites (H-QOE-RANGES)."""
import numpy as np

W = (0.6, 0.25, 0.15)
Q_RANGE = (40.0, 90.0)     # dB, observe Phase C (46-88)
D_RANGE = (0.0, 50.0)      # ms, budget Dmax
E_RANGE = (0.0, 100.0)     # mJ, ref physique Pmax*Dmax = 2W*50ms

def _clip01(x):
    return float(min(1.0, max(0.0, x)))

def normalize(q_db, d_ms, e_mj):
    qn = _clip01((q_db - Q_RANGE[0]) / (Q_RANGE[1] - Q_RANGE[0]))
    dn = _clip01((d_ms - D_RANGE[0]) / (D_RANGE[1] - D_RANGE[0]))
    en = _clip01((e_mj - E_RANGE[0]) / (E_RANGE[1] - E_RANGE[0]))
    return qn, dn, en

def qoe_raw(q_db, d_ms, e_mj, w=W):
    qn, dn, en = normalize(q_db, d_ms, e_mj)
    return w[0] * qn - w[1] * dn - w[2] * en, (qn, dn, en)

def qoe(q_db, d_ms, e_mj, w=W):
    r, _ = qoe_raw(q_db, d_ms, e_mj, w)
    # Ecretage : pour un vecteur de poids quelconque, l'image de
    # (raw+0.4) peut sortir de [0,1] (cf. sensibilite) -> clip explicite.
    return _clip01((r + 0.4) / 1.0)

def manuscript_bound_check():
    return {"min_possible": -W[1] - W[2], "max_possible": W[0],
            "manuscript_claim": "[0,1]", "claim_valid": False}
