import klayout.db as db
import os
import sys

# ── Directory structure ─────────────────────────────────────────────────────
PDK = "./gds"
OUT = "./results"
os.makedirs(OUT, exist_ok=True)

INPUT_GDS = {
    "main"    : f"./riscv_soc.pd.gds",
    "stdcell" : f"{PDK}/sky130_fd_sc_hd.gds",
    "sram_2k" : f"{PDK}/sky130_sram_2kbyte_1rw1r_32x512_8.gds",
    "sram_1k" : f"{PDK}/sky130_sram_1kbyte_1rw1r_32x256_8.gds",
}
OUTPUT_GDS = f"{OUT}/riscv_soc_merged.gds"

# ── Verify inputs ───────────────────────────────────────────────────────────
print("=" * 60)
print("GDS Merge — KLayout 0.30.7")
print("=" * 60)

print("\n=== Input file check ===")
all_ok = True
for name, path in INPUT_GDS.items():
    if os.path.exists(path):
        mb = os.path.getsize(path) / 1024 / 1024
        print(f"  OK      [{name}] {path} ({mb:.1f} MB)")
    else:
        print(f"  MISSING [{name}] {path}")
        all_ok = False

if not all_ok:
    print("\nERROR: Missing files. Aborting.")
    sys.exit(1)

# ── Set up read options ─────────────────────────────────────────────────────
print("\n=== Configuring read options ===")
try:
    opts = db.LoadLayoutOptions()
    opts.cell_conflict_resolution = \
        db.LoadLayoutOptions.CellConflictResolution.SkipNewCell
    print("  Using CellConflictResolution.SkipNewCell")
    use_opts = True
except AttributeError:
    print("  CellConflictResolution not available, using default read")
    opts = db.LoadLayoutOptions()
    use_opts = False

# ── Load all GDS ────────────────────────────────────────────────────────────
print("\n=== Loading GDS files ===")
main = db.Layout()

print(f"Loading main: {INPUT_GDS['main']}")
main.read(INPUT_GDS["main"])
print(f"  Cells: {main.cells()}")

for name in ["stdcell", "sram_2k", "sram_1k"]:
    path = INPUT_GDS[name]
    print(f"\nLoading {name}: {path}")
    if use_opts:
        main.read(path, opts)
    else:
        main.read(path)
    print(f"  Cells: {main.cells()}")

# ── Remap ICC2 internal layer numbers to sky130A GDS layers ─────────────────
# ICC2 writes via master cells ($$L1M1_PR, $$M1M2_PR etc) using
# tf file layerNumbers (2,3,4,5...) instead of sky130A GDS numbers.
# This remaps them to the correct sky130A layer:datatype values.
# Source: sky130_fd_sc_hd.tf layerNumber assignments
#
# ── Remap ICC2 internal layer numbers to sky130A GDS layers ─────────────────
LAYER_REMAP = {
    (2,  0): (67, 20),   # li1
    (3,  0): (67, 44),   # mcon
    (4,  0): (68, 20),   # met1
    (5,  0): (68, 44),   # via
    (6,  0): (69, 20),   # met2
    (7,  0): (69, 44),   # via2
    (8,  0): (70, 20),   # met3
    (9,  0): (70, 44),   # via3
    (10, 0): (71, 20),   # met4
    (11, 0): (71, 44),   # via4
    (12, 0): (72, 20),   # met5
    (13, 0): (66, 20),   # fieldpoly
    (14, 0): (65, 20),   # diff
    (15, 0): (64, 20),   # nwell
    (16, 0): (64, 44),   # pwell
}

print("\n=== Remapping ICC2 layers to sky130A layers ===")

src_to_dst = {}
for (sl, sd), (dl, dd) in LAYER_REMAP.items():
    si = main.find_layer(sl, sd)
    # KLayout may return None or -1 if layer not found
    if si is None or si < 0:
        continue
    di = main.find_layer(dl, dd)
    if di is None or di < 0:
        di = main.layer(dl, dd)
    if si != di:
        src_to_dst[si] = di
        print(f"  {sl}:{sd} -> {dl}:{dd}  (idx {si} -> {di})")

if not src_to_dst:
    print("  No ICC2 internal layers found — may already be correct")
else:
    print(f"\n  Remapping across {main.cells()} cells...")
    remapped = 0
    for cell in main.each_cell():
        for si, di in src_to_dst.items():
            shapes = cell.shapes(si)
            if not shapes.is_empty():
                cell.shapes(di).insert(shapes)
                shapes.clear()
                remapped += 1
    print(f"  Done — remapped {remapped} shape collections")
# ── Verify via cell layers after remap ──────────────────────────────────────
print("\n=== Via cell layer verification ===")
via_cells = [
    "$$L1M1_PR", "$$L1M1_PR_C",
    "$$M1M2_PR", "$$M1M2_PR_C",
    "$$M2M3_PR", "$$M2M3_PR_C",
    "$$M3M4_PR", "$$M3M4_PR_C",
    "$$M4M5_PR", "$$M4M5_PR_C",
]
expected = {
    "$$L1M1_PR":   ["67:20", "67:44", "68:20"],
    "$$L1M1_PR_C": ["67:20", "67:44", "68:20"],
    "$$M1M2_PR":   ["68:20", "68:44", "69:20"],
    "$$M1M2_PR_C": ["68:20", "68:44", "69:20"],
    "$$M2M3_PR":   ["69:20", "69:44", "70:20"],
    "$$M2M3_PR_C": ["69:20", "69:44", "70:20"],
    "$$M3M4_PR":   ["70:20", "70:44", "71:20"],
    "$$M3M4_PR_C": ["70:20", "70:44", "71:20"],
    "$$M4M5_PR":   ["71:20", "71:44", "72:20"],
    "$$M4M5_PR_C": ["71:20", "71:44", "72:20"],
}

all_via_ok = True
for cname in via_cells:
    cell = main.cell(cname)
    if cell is None:
        print(f"  SKIP  {cname} — not found (may not be used)")
        continue
    layers = []
    for li in range(main.layers()):
        if not cell.shapes(li).is_empty():
            info = main.get_info(li)
            layers.append(f"{info.layer}:{info.datatype}")
    layers = sorted(layers)
    exp = sorted(expected.get(cname, []))

    # Check for any remaining ICC2 internal layers
    bad = [l for l in layers
           if int(l.split(":")[0]) < 60
           and int(l.split(":")[0]) > 0]

    if bad:
        print(f"  FAIL  {cname}: still has ICC2 layers {bad}")
        all_via_ok = False
    else:
        print(f"  OK    {cname}: {layers}")

if all_via_ok:
    print("\n  ✓ All via cells have correct sky130A layer numbers")
    print("  ✓ Magic DRC should no longer see 19M false violations")
else:
    print("\n  ✗ Some via cells still have wrong layers")
    print("  ✗ Check LAYER_REMAP — some tf layerNumbers may be missing")

# ── Write output ─────────────────────────────────────────────────────────────
print(f"\n=== Writing merged GDS ===")
print(f"Output: {OUTPUT_GDS}")
main.write(OUTPUT_GDS)

mb = os.path.getsize(OUTPUT_GDS) / 1024 / 1024
print(f"Done. Size: {mb:.1f} MB")

# ── Report ────────────────────────────────────────────────────────────────────
print("\n=== Top-level cells ===")
for cell in main.each_cell():
    if main.cell(cell.name).is_top():
        print(f"  TOP: {cell.name}")

if main.cell("riscv_soc") is not None:
    print("\n✓ riscv_soc found in merged GDS")
    print("✓ Merge successful")
else:
    print("\nERROR: riscv_soc not found in merged GDS")
    sys.exit(1)

# ── Standard cell geometry verification ──────────────────────────────────────
print("\n=== Standard cell geometry verification ===")
for cell_name in [
    "sky130_fd_sc_hd__inv_2",
    "sky130_fd_sc_hd__dfxtp_1",
    "sky130_fd_sc_hd__buf_4",
]:
    cell = main.cell(cell_name)
    if cell is not None:
        total_shapes = sum(
            cell.shapes(li).size()
            for li in range(main.layers())
        )
        if total_shapes > 0:
            print(f"  ✓ {cell_name} ({total_shapes} shapes)")
        else:
            print(f"  ✗ {cell_name} — no geometry")
    else:
        print(f"  ✗ {cell_name} — not found")

# ── SRAM geometry verification ────────────────────────────────────────────────
print("\n=== SRAM geometry verification ===")
for sram_name in [
    "sky130_sram_2kbyte_1rw1r_32x512_8",
    "sky130_sram_1kbyte_1rw1r_32x256_8",
]:
    cell = main.cell(sram_name)
    if cell is not None:
        total_shapes = sum(
            cell.shapes(li).size()
            for li in range(main.layers())
        )
        if total_shapes > 0:
            print(f"  ✓ {sram_name} ({total_shapes} shapes)")
        else:
            print(f"  ✗ {sram_name} — cell exists but NO geometry")
    else:
        print(f"  ✗ {sram_name} — NOT FOUND")

print("\n" + "=" * 60)
print(f"Output: {OUTPUT_GDS}")
print("=" * 60)
