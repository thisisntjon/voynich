"""s123 colour helpers: sRGB -> CIELAB (D65) on the GPU (torch cuda, CPU fallback) and paint-pixel classes.
Imported by tools/s123_calib.py and tools/s123_water_sheet.py. No thresholds live here; callers pass them."""
import numpy as np
from PIL import Image

try:
    import torch
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:  # pragma: no cover
    torch = None
    DEV = "none"

DOWNSAMPLE = 2  # every page is read at 1/2 linear resolution (box filter)


def load_rgb(path, ds=DOWNSAMPLE):
    im = Image.open(path).convert("RGB")
    if ds > 1:
        im = im.resize((im.width // ds, im.height // ds), Image.BOX)
    return np.asarray(im)


def rgb_to_lab(rgb):
    """rgb uint8 HxWx3 -> (L, a, b, C, h_deg) float32 arrays. sRGB D65, standard formulas."""
    if torch is not None:
        x = torch.as_tensor(rgb, device=DEV).float() / 255.0
        lin = torch.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
        M = torch.tensor([[0.4124564, 0.3575761, 0.1804375],
                          [0.2126729, 0.7151522, 0.0721750],
                          [0.0193339, 0.1191920, 0.9503041]], device=lin.device)
        xyz = lin @ M.T
        xyz = xyz / torch.tensor([0.95047, 1.0, 1.08883], device=lin.device)
        e, k = 216 / 24389, 24389 / 27
        f = torch.where(xyz > e, xyz ** (1 / 3), (k * xyz + 16) / 116)
        L = 116 * f[..., 1] - 16
        a = 500 * (f[..., 0] - f[..., 1])
        b = 200 * (f[..., 1] - f[..., 2])
        C = torch.sqrt(a * a + b * b)
        h = torch.rad2deg(torch.atan2(b, a)) % 360
        return tuple(t.cpu().numpy().astype(np.float32) for t in (L, a, b, C, h))
    raise RuntimeError("torch missing")


def classify(L, C, h, th):
    """th: dict L_MIN, L_MAX, C_MIN, H_G_LO, H_SPLIT, H_B_HI. Returns int8 map 0 other, 1 green, 2 blue."""
    paint = (L >= th["L_MIN"]) & (L <= th["L_MAX"]) & (C >= th["C_MIN"])
    g = paint & (h >= th["H_G_LO"]) & (h < th["H_SPLIT"])
    b = paint & (h >= th["H_SPLIT"]) & (h <= th["H_B_HI"])
    out = np.zeros(L.shape, np.int8)
    out[g] = 1
    out[b] = 2
    return out
