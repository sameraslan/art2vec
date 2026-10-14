"""Check the entropic approximation of the palette EMD against the exact linear programme."""
import sys
import numpy as np
from common import ROOT, d_sinkhorn, load_part
sys.path.insert(0, str(ROOT / "experiments" / "painting2vec"))
from features.colour import palette_emd
x = load_part("pilot", "colour__raw", "palette_kmeans")[:40]
s = d_sinkhorn(x, x)
e = np.array([[palette_emd(a, b) for b in x] for a in x])
m = ~np.eye(40, dtype=bool)
print("pearson", np.corrcoef(s[m], e[m])[0, 1], "median rel err", np.median(np.abs(s[m] - e[m]) / e[m]), "max rel err", np.max(np.abs(s[m] - e[m]) / e[m]))
from scipy.stats import spearmanr
print("spearman", spearmanr(s[m], e[m])[0])
