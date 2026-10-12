"""Canal 28 GHz : pathloss III-B, Rayleigh, Shannon, Doppler, file M/D/1."""
import numpy as np

C = 3e8

def pathloss_db(d_m, eta=2.8, d0=1.0, PL0=61.4, sigma=8.2, rng=None):
    rng = np.random.default_rng() if rng is None else rng
    return PL0 + 10 * eta * np.log10(np.maximum(d_m, d0) / d0) + rng.normal(0, sigma)

def doppler_hz(v_kmh, fc_hz=28e9):
    return (v_kmh / 3.6) * fc_hz / C  # radial max ; 10 km/h @28 GHz -> ~259 Hz

def step_rate_bps(P_w, bw_hz, d_m, N0_dbm_hz=-174.0, rng=None, eta=2.8, sigma=8.2):
    rng = np.random.default_rng() if rng is None else rng
    pl = pathloss_db(d_m, eta=eta, sigma=sigma, rng=rng)
    g = (rng.normal() + 1j * rng.normal()) / np.sqrt(2)  # Rayleigh CN(0,1)
    h2 = (10 ** (-pl / 10)) * abs(g) ** 2
    N0 = 10 ** ((N0_dbm_hz - 30) / 10)  # W/Hz
    snr = P_w * h2 / (N0 * bw_hz)
    return float(bw_hz * np.log2(1 + snr)), float(snr), float(pl)

def queue_md1_ms(lam=30.0, mu=None):
    """M/D/1 : retourne (Dqueue_ms, rho). mu en trames/s."""
    if mu is None or mu <= 0:
        return 1000.0, 99.0
    rho = lam / mu
    if rho >= 1.0:
        return 1000.0, float(rho)  # saturation : plafond documente
    return float(rho / (2 * mu * (1 - rho)) * 1000.0), float(rho)
