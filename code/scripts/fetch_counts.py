import os as _os
SUPP_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
import sys as _sys
if _os.path.join(SUPP_ROOT, "code") not in _sys.path:
    _sys.path.insert(0, _os.path.join(SUPP_ROOT, "code"))
#!/usr/bin/env python3
"""Phase A — recupere les 4 Counts.txt distants (via Range, comme l'audit) et
calcule les statistiques completes. Donnees: METADONNEES fournisseur (pas de
mesure point par point). Ecrit results/counts_full.csv + resume JSON stdout."""
import struct, subprocess, zlib, csv, json, statistics

URLS = {
 "longdress": "https://plenodb.jpeg.org/pc/8ilabs/longdress.zip",
 "loot": "https://plenodb.jpeg.org/pc/8ilabs/loot.zip",
 "redandblack": "https://plenodb.jpeg.org/pc/8ilabs/redandblack.zip",
 "soldier": "https://plenodb.jpeg.org/pc/8ilabs/soldier.zip",
}

def curl_range(url, a, b, timeout=120):
    p = subprocess.run(["curl.exe","-sS","-L","--max-time",str(timeout),
                        "-H",f"Range: bytes={a}-{b}",url], capture_output=True)
    assert p.returncode == 0, p.stderr.decode()[:200]
    return p.stdout

def get_cd(url):
    h = subprocess.run(["curl.exe","-sS","-I","-L","--max-time","30",url],
                       capture_output=True, text=True).stdout
    size = int([l for l in h.splitlines() if l.lower().startswith("content-length:")][0].split(":")[1].strip())
    tail = curl_range(url, size-300000, size-1)
    idx = tail.rfind(b"\x50\x4b\x05\x06")
    (_s,_a,_b,_c,ctotal,csize,coff,_cl) = struct.unpack("<IHHHHIIH", tail[idx:idx+22])
    cd = curl_range(url, coff, coff+csize-1)
    pos=0; infos=[]
    while pos < len(cd):
        f = struct.unpack("<HHHHHHIIIHHHHHII", cd[pos+4:pos+46])
        fnl,efl,fcl,lo = f[9],f[10],f[11],f[15]
        infos.append(dict(name=cd[pos+46:pos+46+fnl].decode(), method=f[3], comp=f[7], uncomp=f[8], local_off=lo))
        pos += 46+fnl+efl+fcl
    return size, infos

def fetch(url, info):
    lo = info["local_off"]
    lh = curl_range(url, lo, lo+29)
    fnl,efl = struct.unpack("<H",lh[26:28])[0], struct.unpack("<H",lh[28:30])[0]
    blob = curl_range(url, lo+30+fnl+efl, lo+30+fnl+efl+info["comp"]-1)
    return zlib.decompress(blob,-15) if info["method"]==8 else blob

rows = []
summary = {}
for seq, url in URLS.items():
    _, infos = get_cd(url)
    ct = [i for i in infos if i["name"].endswith("Counts.txt")][0]
    lines = fetch(url, ct).decode("ascii").splitlines()
    vals = []
    for ln in lines:
        p = ln.split()
        vals.append((int(p[0]), p[1]))
        rows.append({"sequence":seq,"frame_file":p[1],"points_counts_txt":int(p[0]),"provenance":"fournisseur-Counts.txt"})
    ns = sorted(n for n,_ in vals)
    q = statistics.quantiles(ns, n=4)
    summary[seq] = {"n":len(ns),"min":min(ns),"q1":q[0],"median":statistics.median(ns),
                    "q3":q[2],"max":max(ns),"mean":round(statistics.mean(ns),1),
                    "stdev":round(statistics.pstdev(ns),1)}
    print(seq, summary[seq])

with open(os.path.join(SUPP_ROOT, "results", "counts_full.csv"),"w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sequence","frame_file","points_counts_txt","provenance"])
    w.writeheader(); w.writerows(rows)
with open(os.path.join(SUPP_ROOT, "results", "counts_summary.json"),"w") as f:
    json.dump(summary, f, indent=2)
print("OK", len(rows))
