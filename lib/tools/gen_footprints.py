"""Generate the STYX32 connector footprints (STYX32.pretty).

Run with KiCad 10's python:
  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" lib/tools/gen_footprints.py [name-filter]

Each footprint is a copy of a base IDC box header footprint (KiCad stock 2.54 mm, Kiu's
Connector_IDC_127 for 1.27 mm SMD) with the STYX32 pin names on F.Fab and the connector marking
(e.g. S32B2) on the silkscreen. 1.27 mm THT uses the 1.27 mm SMD body with through-hole
pads for the HANXIA HX JN1.27-2xNP ZZ H4.9 (0.4 mm square pins on a 1.27 mm grid).
KiCad writes the files, so they are always in its own format.
"""
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.normpath(os.path.join(HERE, "..", "STYX32.pretty"))
STOCK = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_IDC.pretty"
IDC127 = r"C:\Users\kiu\Documents\projects\kicad\internal\Connector_IDC_127\Connector_IDC_127.pretty"
# 1.27 mm models ship with this library (make_3d.py); users set the path variable STYX32_LIB
# to the lib folder (KiCad: Preferences > Configure Paths)
MODELS127 = "${STYX32_LIB}/STYX32.3dshapes"

# Silkscreen pin names (same abbreviations as on the STYX32 board)
CONNECTORS = {
    "A":  ["3V3", "TX", "RES", "RX", "GND", "BOOT"],
    "B1": ["3V3", "SWDIO", "RES", "SWDCLK", "GND", "TX"],
    "B2": ["3V3", "SWDIO", "RES", "SWDCLK", "GND", "SWO"],
    "C":  ["3V3", "SWDIO", "RES", "SWDCLK", "GND", "SWO", "TX", "RX"],
    "D":  ["3V3", "SWDIO", "GND", "SWDCLK", "GND", "SWO", "NC", "TDI", "GND", "RES"],
}
VARIANTS = ["P2.54mm_THT", "P2.54mm_SMD", "P1.27mm_THT", "P1.27mm_SMD"]

TEXT_H = 0.8      # silk text height (JLC minimum 0.8 mm)
TEXT_W = 0.12     # stroke
GAP = 0.5         # distance from body/pads to the pin names
SOURCE = "https://github.com/kiu/STYX32"
KEY_HALF = {"P2.54mm": 2.05, "P1.27mm": 1.225}   # half width of the key notch (stock 4.1 / HANXIA 2.45)
MARK_H = 1.5      # connector marking S32A, S32B2, ...
MARK_W = 0.25


def mm(v):
    return pcbnew.FromMM(v)


def base_footprint(rows, variant):
    if variant == "P2.54mm_THT":
        return pcbnew.FootprintLoad(STOCK, "IDC-Header_2x%02d_P2.54mm_Vertical" % rows)
    if variant == "P2.54mm_SMD":
        return pcbnew.FootprintLoad(STOCK, "IDC-Header_2x%02d_P2.54mm_Vertical_SMD" % rows)
    fp = pcbnew.FootprintLoad(IDC127, "IDC-Header_2x%02d_P1.27mm_Vertical_SMD" % rows)
    if variant == "P1.27mm_SMD":
        return fp
    # 1.27 mm THT: same body, pins at x = -/+0.635 instead of SMD pads at -/+2
    for pad in list(fp.Pads()):
        pos = pad.GetPosition()
        x = -0.635 if pcbnew.ToMM(pos.x) < 0 else 0.635
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        pad.SetLayerSet(pad.PTHMask())
        pad.SetShape(pcbnew.F_Cu, pcbnew.PAD_SHAPE_RECTANGLE if pad.GetNumber() == "1" else pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
        pad.SetDrillSize(pcbnew.VECTOR2I(mm(0.65), mm(0.65)))
        pad.SetPosition(pcbnew.VECTOR2I(mm(x), pos.y))
    fp.SetAttributes(pcbnew.FP_THROUGH_HOLE)
    # silk and courtyard of the SMD version go around the pads: redraw them around the body
    fab = [i.GetBoundingBox() for i in fp.GraphicalItems()
           if i.GetLayer() == pcbnew.F_Fab and i.GetClass() != "PCB_TEXT"]
    bx0, by0 = (pcbnew.ToMM(min(getattr(b, g)() for b in fab)) for g in ("GetLeft", "GetTop"))
    bx1, by1 = (pcbnew.ToMM(max(getattr(b, g)() for b in fab)) for g in ("GetRight", "GetBottom"))
    for item in list(fp.GraphicalItems()):
        if item.GetLayer() in (pcbnew.F_SilkS, pcbnew.F_CrtYd) and item.GetClass() != "PCB_TEXT":
            fp.Remove(item)
    # silk outline with the key notch drawn in, like KiCad's 2.54 mm THT footprints
    sx0, sy0, sx1, sy1 = bx0 - 0.11, by0 - 0.11, bx1 + 0.11, by1 + 0.11
    cy, h, d = (by0 + by1) / 2, KEY_HALF["P1.27mm"], 0.8
    pts = [(sx0, cy - h), (sx0, sy0), (sx1, sy0), (sx1, sy1), (sx0, sy1), (sx0, cy + h),
           (sx0 + d, cy + h), (sx0 + d, cy - h), (sx0, cy - h)]
    for a, b in zip(pts, pts[1:]):
        seg(fp, pcbnew.F_SilkS, 0.12, *a, *b)
    rect(fp, pcbnew.F_CrtYd, 0.05, bx0 - 0.5, by0 - 0.5, bx1 + 0.5, by1 + 0.5)
    # pin 1 marker: triangle left of the body, pointing at pin 1
    triangle(fp, bx0 - 0.4, pcbnew.ToMM(min(p.GetPosition().y for p in fp.Pads())))
    return fp


def triangle(fp, tx, ty):
    """Pin 1 marker: silk triangle with its tip at (tx, ty), pointing right."""
    for a, b in (((tx - 0.6, ty - 0.4), (tx, ty)), ((tx, ty), (tx - 0.6, ty + 0.4)),
                 ((tx - 0.6, ty + 0.4), (tx - 0.6, ty - 0.4))):
        seg(fp, pcbnew.F_SilkS, 0.12, *a, *b)


def seg(fp, layer, width, xa, ya, xb, yb):
    s = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(mm(xa), mm(ya)))
    s.SetEnd(pcbnew.VECTOR2I(mm(xb), mm(yb)))
    s.SetLayer(layer)
    s.SetWidth(mm(width))
    fp.Add(s)


def bar(fp, xa, ya, xb, yb):
    """Filled silk rectangle."""
    s = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_RECT)
    s.SetStart(pcbnew.VECTOR2I(mm(xa), mm(ya)))
    s.SetEnd(pcbnew.VECTOR2I(mm(xb), mm(yb)))
    s.SetLayer(pcbnew.F_SilkS)
    s.SetWidth(mm(0.1))
    s.SetFilled(True)
    fp.Add(s)


def fab_box(fp):
    """Bounding box of the body outline on F.Fab, in mm: x0, y0, x1, y1."""
    bbs = [i.GetBoundingBox() for i in fp.GraphicalItems()
           if i.GetLayer() == pcbnew.F_Fab and i.GetClass() != "PCB_TEXT"]
    return [pcbnew.ToMM(v) for v in (min(b.GetLeft() for b in bbs), min(b.GetTop() for b in bbs),
                                     max(b.GetRight() for b in bbs), max(b.GetBottom() for b in bbs))]


def rect(fp, layer, width, xa, ya, xb, yb):
    for a, b in (((xa, ya), (xb, ya)), ((xb, ya), (xb, yb)), ((xb, yb), (xa, yb)), ((xa, yb), (xa, ya))):
        seg(fp, layer, width, *a, *b)


def body_box(fp):
    """Bounding box of the body (F.Fab) and pads, in mm: x0, y0, x1, y1."""
    xs, ys = [], []
    for item in fp.GraphicalItems():
        if item.GetLayer() in (pcbnew.F_Fab, pcbnew.F_SilkS) and item.GetClass() != "PCB_TEXT":
            bb = item.GetBoundingBox()
            xs += [bb.GetLeft(), bb.GetRight()]
            ys += [bb.GetTop(), bb.GetBottom()]
    for pad in fp.Pads():
        p, s = pad.GetPosition(), pad.GetSize(pcbnew.F_Cu)
        xs += [p.x - s.x // 2, p.x + s.x // 2]
        ys += [p.y - s.y // 2, p.y + s.y // 2]
    return [pcbnew.ToMM(v) for v in (min(xs), min(ys), max(xs), max(ys))]


def add_text(fp, text, x, y, hjust, h=TEXT_H, w=TEXT_W, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(fp)
    t.SetText(text)
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(h), mm(h)))
    t.SetTextThickness(mm(w))
    t.SetHorizJustify(hjust)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    fp.Add(t)


def build(conn, variant, out_lib):
    names = CONNECTORS[conn]
    rows = len(names) // 2
    fp = base_footprint(rows, variant)
    name = "STYX32_%s_2x%02d_%s" % (conn, rows, variant)
    fp.SetFPID(pcbnew.LIB_ID("", name))
    fp.SetLibDescription("STYX32 %s connector, IDC box header 2x%02d, %s %s" % (
        conn, rows, variant[1:5] + " mm pitch", variant[-3:]))
    fp.SetKeywords("STYX32 %s IDC box header %s" % (conn, variant.replace("_", " ")))
    fp.Value().SetText(name)

    # centre line of the body: reference and marking are centred on it
    fx0, fy0, fx1, fy1 = fab_box(fp)
    cx, cy = (fx0 + fx1) / 2, (fy0 + fy1) / 2

    if variant.endswith("SMD"):
        # key notch: the pads cover the body wall, so mark the notch with a bar next to it,
        # and (2.54 mm, no pin 1 mark on the stock silkscreen) a triangle at pin 1
        xl = min(fx0, min(pcbnew.ToMM(p.GetPosition().x - p.GetSize(pcbnew.F_Cu).x // 2) for p in fp.Pads()))
        h = KEY_HALF[variant[:7]]
        bar(fp, xl - 0.75, cy - h, xl - 0.35, cy + h)
        if variant == "P2.54mm_SMD":
            p1 = [p for p in fp.Pads() if p.GetNumber() == "1"][0]
            triangle(fp, xl - 1.0, pcbnew.ToMM(p1.GetPosition().y))

    fp.SetField("Source", SOURCE)
    fp.GetField("Source").SetVisible(False)

    x0, y0, x1, y1 = body_box(fp)
    for pad in fp.Pads():
        num = int(pad.GetNumber())
        px, py = (pcbnew.ToMM(v) for v in (pad.GetPosition().x, pad.GetPosition().y))
        if px < cx:
            add_text(fp, names[num - 1], x0 - GAP, py, pcbnew.GR_TEXT_H_ALIGN_RIGHT, layer=pcbnew.F_Fab)
        else:
            add_text(fp, names[num - 1], x1 + GAP, py, pcbnew.GR_TEXT_H_ALIGN_LEFT, layer=pcbnew.F_Fab)

    # Marking (short form S32<conn>, larger than the pin names) below the body, reference above it
    add_text(fp, "S32" + conn, cx, y1 + GAP + MARK_H / 2 + 0.4, pcbnew.GR_TEXT_H_ALIGN_CENTER, MARK_H, MARK_W)
    fp.Reference().SetPosition(pcbnew.VECTOR2I(mm(cx), mm(y0 - GAP - 0.8)))
    fp.Value().SetPosition(pcbnew.VECTOR2I(mm(cx), mm(y1 + GAP + MARK_H + 1.7)))

    if variant.startswith("P1.27mm"):
        # Models() hands out copies: replace the whole list
        model = pcbnew.FP_3DMODEL()
        model.m_Filename = "%s/IDC-Header_2x%02d_P1.27mm_Vertical_%s.wrl" % (MODELS127, rows, variant[-3:])
        fp.Models().clear()
        fp.Models().push_back(model)

    pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP).FootprintSave(out_lib, fp)
    print("wrote", name)


def main():
    flt = sys.argv[1] if len(sys.argv) > 1 else ""
    os.makedirs(LIB, exist_ok=True)
    for conn in CONNECTORS:
        for variant in VARIANTS:
            name = "STYX32_%s_%s" % (conn, variant)
            if flt in name:
                build(conn, variant, LIB)


if __name__ == "__main__":
    main()
