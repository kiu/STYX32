"""Generate the STYX32 connector symbols (STYX32.kicad_sym).

Run with any Python 3:
  python lib/tools/gen_symbols.py

Writes the whole library from scratch: one symbol per connector and footprint variant, drawn
like KiCad's Connector_Generic Conn_02xNN_Odd_Even (5.08 mm body, pin names hidden), centred on
the origin with Reference above and Value below the body. Each symbol links its footprint
(STYX32.pretty, made by gen_footprints.py) and carries LCSC, datasheet, description and source.
Check afterwards: kicad-cli sym export svg -o <dir> lib/STYX32.kicad_sym
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "STYX32.kicad_sym"))
SOURCE = "https://github.com/kiu/STYX32"

# pin names in pin order (1, 2, 3, ...); odd pins left, even pins right
CONNECTORS = {
    "A":  ("serial (TX, RX, BOOT0)",
           ["3V3", "TX", "RESET", "RX", "GND", "BOOT0"]),
    "B1": ("SWD with serial TX on pin 6",
           ["3V3", "SWDIO", "RESET", "SWDCLK", "GND", "TX"]),
    "B2": ("SWD with SWO on pin 6",
           ["3V3", "SWDIO", "RESET", "SWDCLK", "GND", "SWO"]),
    "C":  ("SWD with SWO plus serial (TX, RX)",
           ["3V3", "SWDIO", "RESET", "SWDCLK", "GND", "SWO", "TX", "RX"]),
    "D":  ("ARM Cortex 10-pin debug (SWD/JTAG)",
           ["3V3", "SWDIO", "GND", "SWDCLK", "GND", "SWO", "KEY", "TDI", "GND", "RESET"]),
}
NO_CONNECT = {"KEY"}
VARIANTS = ["P2.54mm_THT", "P2.54mm_SMD", "P1.27mm_THT", "P1.27mm_SMD"]
EDGE = list(CONNECTORS)   # connectors with a card edge footprint (gen_footprints.py EDGE)
# card edge: no part on the board; Mate = the matching edge slot socket (WingTAT ED0xBGFBK)
MATE = {3: "C5173287", 4: "C5173288", 5: "C5173289"}
LCSC = {  # (rows, variant) -> LCSC part number
    (3, "P2.54mm_THT"): "C492441", (3, "P2.54mm_SMD"): "C492445",
    (3, "P1.27mm_THT"): "C42372545", (3, "P1.27mm_SMD"): "C42372553",
    (4, "P2.54mm_THT"): "C17179451", (4, "P2.54mm_SMD"): "C601965",
    (4, "P1.27mm_THT"): "C42372546", (4, "P1.27mm_SMD"): "C42372554",
    (5, "P2.54mm_THT"): "C5665", (5, "P2.54mm_SMD"): "C492446",
    (5, "P1.27mm_THT"): "C42372547", (5, "P1.27mm_SMD"): "C42372555",
}

BODY_X = 2.54      # half body width (stock: 5.08 mm)
STUB_X = 1.27      # inner end of the pin stubs drawn in the body
PIN_X = 6.35       # pin end
PIN_LEN = 3.81
TEXT_GAP = 2.54    # body edge to Reference/Value


def fmt(v):
    v = round(v, 4)
    return ("%.4f" % v).rstrip("0").rstrip(".") if v != int(v) else str(int(v))


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def prop(name, value, x, y, hide=False):
    return ('\t\t(property "%s" "%s"\n\t\t\t(at %s %s 0)\n%s'
            '\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n'
            '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
            % (name, esc(value), fmt(x), fmt(y), "\t\t\t(hide yes)\n" if hide else ""))


def rect(x0, y0, x1, y1, width, fill):
    return ('\t\t\t(rectangle\n\t\t\t\t(start %s %s)\n\t\t\t\t(end %s %s)\n'
            '\t\t\t\t(stroke\n\t\t\t\t\t(width %s)\n\t\t\t\t\t(type default)\n\t\t\t\t)\n'
            '\t\t\t\t(fill\n\t\t\t\t\t(type %s)\n\t\t\t\t)\n\t\t\t)\n'
            % (fmt(x0), fmt(y0), fmt(x1), fmt(y1), fmt(width), fill))


def pin(etype, x, y, angle, name, number):
    font = '\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n'
    return ('\t\t\t(pin %s line\n\t\t\t\t(at %s %s %s)\n\t\t\t\t(length %s)\n'
            '\t\t\t\t(name "%s"\n\t\t\t\t\t(effects\n%s\t\t\t\t\t)\n\t\t\t\t)\n'
            '\t\t\t\t(number "%s"\n\t\t\t\t\t(effects\n%s\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n'
            % (etype, fmt(x), fmt(y), angle, fmt(PIN_LEN), esc(name), font, number, font))


def symbol(conn, variant):
    what, names = CONNECTORS[conn]
    rows = len(names) // 2
    name = "STYX32_%s_2x%02d_%s" % (conn, rows, variant)
    edge = variant == "P2.54mm_Edge"
    lcsc = MATE[rows] if edge else LCSC[(rows, variant)]
    # pin rows on the 2.54 mm grid, pin 1 on top (5 rows: centred, else top row at +2.54)
    ys = [2.54 * ((2 if rows == 5 else 1) - i) for i in range(rows)]
    top, bottom = ys[0] + 1.27, ys[-1] - 1.27
    if edge:
        desc = ("STYX32 %s connector: %s. Card edge (gold fingers) 2x%02d, 2.54 mm pitch, "
                "mates with edge slot %s" % (conn, what, rows, lcsc))
    else:
        desc = "STYX32 %s connector: %s. IDC box header 2x%02d, %s pitch, %s" % (
            conn, what, rows, variant[1:7], variant[-3:])

    out = ['\t(symbol "%s"\n' % name,
           '\t\t(pin_names\n\t\t\t(offset 1.016)\n\t\t\t(hide yes)\n\t\t)\n',
           '\t\t(exclude_from_sim no)\n\t\t(in_bom %s)\n\t\t(on_board yes)\n\t\t(in_pos_files %s)\n'
           '\t\t(duplicate_pin_numbers_are_jumpers no)\n' % (("no", "no") if edge else ("yes", "yes")),
           prop("Reference", "J", 0, top + TEXT_GAP),
           prop("Value", "STYX32_" + conn, 0, bottom - TEXT_GAP),
           prop("Footprint", "STYX32:" + name, 0, 0, True),
           prop("Datasheet", "https://www.lcsc.com/datasheet/%s.pdf" % lcsc, 0, 0, True),
           prop("Description", desc, 0, 0, True),
           prop("Source", SOURCE, 0, 0, True),
           prop("Mate" if edge else "LCSC", lcsc, 0, 0, True),
           prop("ki_keywords", "connector STYX32 " + ("card edge gold finger" if edge else "IDC"), 0, 0, True),
           prop("ki_fp_filters", "STYX32*", 0, 0, True)]

    out.append('\t\t(symbol "%s_0_1"\n' % name)
    out.append(rect(-BODY_X, top, BODY_X, bottom, 0.254, "background"))
    for y in ys:
        out.append(rect(-BODY_X, y + 0.127, -STUB_X, y - 0.127, 0.1524, "none"))
        out.append(rect(BODY_X, y + 0.127, STUB_X, y - 0.127, 0.1524, "none"))
    out.append('\t\t)\n')

    out.append('\t\t(symbol "%s_1_1"\n' % name)
    for i, y in enumerate(ys):
        for side, num in ((0, 2 * i + 1), (1, 2 * i + 2)):
            pname = names[num - 1]
            etype = "no_connect" if pname in NO_CONNECT else "passive"
            out.append(pin(etype, PIN_X if side else -PIN_X, y, 180 if side else 0, pname, num))
    out.append('\t\t)\n\t\t(embedded_fonts no)\n\t)\n')
    return "".join(out)


def main():
    syms = [symbol(c, v) for c in CONNECTORS for v in VARIANTS + (["P2.54mm_Edge"] if c in EDGE else [])]
    body = "".join(syms)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write('(kicad_symbol_lib\n\t(version 20251024)\n\t(generator "gen_symbols.py")\n'
                '\t(generator_version "10.0")\n' + body + ')\n')
    print("wrote", OUT, len(syms), "symbols")


if __name__ == "__main__":
    main()
