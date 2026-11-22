"""Shift whole columns of the template schematic sideways (one-off layout tool).

  python lib/tools/shift_columns.py lib/template/template.kicad_sch [--apply]

Every top-level item (symbol, wire, label, junction, text, no-connect) whose x lies in a column
range is moved by that column's dx: only the x of its "(at x y" and "(xy x y)" coordinates
changes, nothing else. lib_symbols and the sheet's own data are left alone. KiCad must be closed.
"""
import re
import shutil
import sys

# (x from, x to, dx): columns 2..4 at 185.42 / 274.32 / 363.22 -> spacing 68.58 mm
COLUMNS = [(141.0, 230.0, -20.32), (230.0, 319.0, -40.64), (319.0, 410.0, -60.96)]
MOVABLE = ("symbol", "wire", "global_label", "label", "junction", "text", "no_connect")


def top_level(text):
    """Yield (start, end, name) of the top-level nodes inside (kicad_sch ...)."""
    depth, start, i, q = 0, None, 0, False
    while i < len(text):
        c = text[i]
        if q:
            if c == "\\":
                i += 1
            elif c == '"':
                q = False
        elif c == '"':
            q = True
        elif c == "(":
            depth += 1
            if depth == 2:
                start = i
        elif c == ")":
            if depth == 2:
                yield start, i + 1, re.match(r"\((\w+)", text[start:start + 40]).group(1)
            depth -= 1
        i += 1


def fmt(v):
    v = round(v, 4)
    return str(int(v)) if v == int(v) else ("%.4f" % v).rstrip("0")


def main():
    path, apply = sys.argv[1], "--apply" in sys.argv
    text = open(path, encoding="utf-8").read()
    out, last, moved = [], 0, {}
    for s, e, name in top_level(text):
        if name not in MOVABLE:
            continue
        node = text[s:e]
        xs = [float(m) for m in re.findall(r"\((?:at|xy) (-?[\d.]+) ", node)]
        dxs = {dx for x in xs for a, b, dx in COLUMNS if a <= x < b}
        if not dxs:
            continue
        if len(dxs) > 1 or any(not any(a <= x < b for a, b, _ in COLUMNS) for x in xs):
            sys.exit("item spans columns: %s" % node[:200])
        dx = dxs.pop()
        node = re.sub(r"\((at|xy) (-?[\d.]+) ", lambda m: "(%s %s " % (m.group(1), fmt(float(m.group(2)) + dx)), node)
        out += [text[last:s], node]
        last = e
        moved[name] = moved.get(name, 0) + 1
    out.append(text[last:])
    print("moved:", moved)
    if apply:
        shutil.copy(path, path + ".bak-shift")
        open(path, "w", encoding="utf-8", newline="\n").write("".join(out))
        print("written, backup", path + ".bak-shift")


if __name__ == "__main__":
    main()
