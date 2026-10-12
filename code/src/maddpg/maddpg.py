"""MADDPG numpy (CPU) : acteurs/critiques MLP + Adam manuel, buffer, cibles Polyak.
Echelle pilote : obs 5-dims, actions (p, bw_logit, alpha) par agent."""
import numpy as np


def relu(x):
    return np.maximum(x, 0)


class MLP:
    def __init__(self, dims, seed=0, out_act="linear"):
        rng = np.random.default_rng(seed)
        self.W = [rng.normal(0, np.sqrt(2 / dims[i]), (dims[i], dims[i + 1])) for i in range(len(dims) - 1)]
        self.b = [np.zeros(dims[i + 1]) for i in range(len(dims) - 1)]
        self.out_act = out_act
        self.mW = [np.zeros_like(w) for w in self.W]
        self.vW = [np.zeros_like(w) for w in self.W]
        self.mb = [np.zeros_like(b) for b in self.b]
        self.vb = [np.zeros_like(b) for b in self.b]
        self.t = 0

    def forward(self, x):
        self.cache = [x]
        a = x
        for i, (w, b) in enumerate(zip(self.W, self.b)):
            z = a @ w + b
            last = i == len(self.W) - 1
            a = z if (last and self.out_act == "linear") else (np.tanh(z) if last else relu(z))
            self.cache.append(a)
        return a

    def backward(self, grad_out, lr=1e-3):
        g = grad_out
        for i in reversed(range(len(self.W))):
            last = i == len(self.W) - 1
            a_prev = self.cache[i]
            if not last:
                g = g * (self.cache[i + 1] > 0)
            else:
                if self.out_act == "tanh":
                    g = g * (1 - self.cache[i + 1] ** 2)
            gW = a_prev.T @ g / max(1, len(a_prev))
            gb = g.mean(axis=0)
            g = g @ self.W[i].T
            self.t += 1
            for arr, m, v, gg in ((self.W[i], self.mW[i], self.vW[i], gW),
                                  (self.b[i], self.mb[i], self.vb[i], gb)):
                m[:] = 0.9 * m + 0.1 * gg
                v[:] = 0.999 * v + 0.001 * gg ** 2
                arr += lr * (m / (1 - 0.9 ** self.t)) / (np.sqrt(v / (1 - 0.999 ** self.t)) + 1e-8)

    def soft_update_from(self, src, tau=0.01):
        for a, b in zip(self.W + self.b, src.W + src.b):
            a[:] = tau * b + (1 - tau) * a

    def hard_copy_from(self, src):
        for a, b in zip(self.W + self.b, src.W + src.b):
            a[:] = b


class MADDPG:
    def __init__(self, n_agents=4, obs_dim=5, act_dim=3, seed=0, actor_lr=1e-3,
                 critic_lr=1e-3, gamma=0.95, tau=0.01, buffer=20000, batch=128,
                 shared_actor=False):
        self.n, self.od, self.ad = n_agents, obs_dim, act_dim
        self.gamma, self.tau, self.batch = gamma, tau, batch
        self.actor_lr, self.critic_lr = actor_lr, critic_lr
        self.actors = [MLP([obs_dim, 32, 32, act_dim], seed + i, "tanh") for i in range(n_agents)]
        if shared_actor:
            # ablation mono-agent centralisee : un seul acteur partage (DDPG-like)
            self.actors = [self.actors[0]] * n_agents
        self.tactors = [MLP([obs_dim, 32, 32, act_dim], seed + 100 + i, "tanh") for i in range(n_agents)]
        jdim = n_agents * (obs_dim + act_dim)
        self.critic = MLP([jdim, 64, 64, 1], seed + 200)
        self.tcritic = MLP([jdim, 64, 64, 1], seed + 300)
        for a, t in zip(self.actors, self.tactors):
            t.hard_copy_from(a)
        self.tcritic.hard_copy_from(self.critic)
        self.buf = []
        self.cap = buffer
        self.rng = np.random.default_rng(seed + 999)

    def act(self, obs, noise=0.0):
        out = []
        for i, a in enumerate(self.actors):
            u = a.forward(obs[i][None, :])[0]
            if noise > 0:
                u = u + self.rng.normal(0, noise, u.shape)
            out.append(np.tanh(u))  # borne [-1,1]
        return np.array(out)

    def map_actions(self, u):
        """u in [-1,1]^3 -> (P_w in [0.1,2], bw_share logit, alpha in [0.02,0.5])."""
        p = 0.1 + 1.9 * (u[:, 0] * 0.5 + 0.5)
        e = np.exp(u[:, 1] - u[:, 1].max())
        shares = e / e.sum()
        alpha = 0.02 + 0.48 * (u[:, 2] * 0.5 + 0.5)
        return p, shares, alpha

    def store(self, o, u, r, o2):
        self.buf.append((o.copy(), u.copy(), float(r), o2.copy()))
        if len(self.buf) > self.cap:
            self.buf.pop(0)

    def update(self):
        if len(self.buf) < self.batch:
            return None
        idx = self.rng.choice(len(self.buf), self.batch, replace=False)
        O = np.array([self.buf[i][0] for i in idx])      # (B,n,od)
        U = np.array([self.buf[i][1] for i in idx])      # (B,n,ad)
        R = np.array([self.buf[i][2] for i in idx])      # (B,)
        O2 = np.array([self.buf[i][3] for i in idx])
        B = len(idx)
        with np.errstate(all="ignore"):
            U2 = np.stack([self.tactors[i].forward(O2[:, i]) for i in range(self.n)], axis=1)
        J2 = np.concatenate([O2.reshape(B, -1), U2.reshape(B, -1)], axis=1)
        yt = (R + self.gamma * self.tcritic.forward(J2)[:, 0])
        J = np.concatenate([O.reshape(B, -1), U.reshape(B, -1)], axis=1)
        q = self.critic.forward(J)[:, 0]
        err = (q - yt)[:, None]
        self.critic.backward(2 * err / B, lr=self.critic_lr)
        for i in range(self.n):
            Ui = self.actors[i].forward(O[:, i])
            Jat = np.concatenate([O.reshape(B, -1)] + [Ui if j == i else U[:, j] for j in range(self.n)], axis=1)
            qv = self.critic.forward(Jat)
            # gradient acteur : dQ/da_i via differences finies sur le critique (simple, robuste)
            g = np.zeros_like(Ui)
            eps = 1e-2
            for k in range(self.ad):
                Up = U.copy(); Up[:, i, k] += eps
                Jp = np.concatenate([O.reshape(B, -1), Up.reshape(B, -1)], axis=1)
                g[:, k] = (self.critic.forward(Jp)[:, 0] - qv[:, 0]) / eps
            # remonte a travers tanh de sortie : on optimise pre-activation via chaine du MLP
            pre = self.actors[i].cache[-1]  # sortie tanh
            g_pre = g * (1 - pre ** 2)
            # backward manuel jusqu'aux poids : rejoue forward pour remplir le cache
            self.actors[i].forward(O[:, i])
            self.actors[i].backward(-g_pre / B, lr=self.actor_lr)
            self.tactors[i].soft_update_from(self.actors[i], self.tau)
        self.tcritic.soft_update_from(self.critic, self.tau)
        return float((err ** 2).mean())
