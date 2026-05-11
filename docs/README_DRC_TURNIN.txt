DRC Turn-in Files — RISC-V SoC

Top cell:
riscv_soc

Main DRC/LVS working folder:
Project-main/flow_scripts/DRC_LVS

DRC flow completed:
1. ICC2 output GDS was copied into DRC_LVS/riscv_soc.pd.gds.
2. merge_gds.py merged the ICC2 GDS with:
   - gds/sky130_fd_sc_hd.gds
   - gds/sky130_sram_1kbyte_1rw1r_32x256_8.gds
   - gds/sky130_sram_2kbyte_1rw1r_32x512_8.gds
3. KLayout DRC was run using:
   - klayout/drc/sky130A_mr.drc
   - Ruby-enabled KLayout installed under final_project_full_with_libs/klayout_ruby

Key DRC outputs:
- riscv_soc_merged.gds
- klayout_drc.log
- klayout_drc_official.lyrdb

Supporting files:
- merge_gds_klayout_r.log
- merge_gds.py
- run_klayout.sh
- riscv_soc.pd.gds
- riscv_soc.pd.v

Note:
LVS was also run later, but LVS did not pass because Magic extraction did not preserve top-level port labels in the extracted layout SPICE. Device counts matched after fixing sky130A_setup.tcl, but top-level pin matching failed.
