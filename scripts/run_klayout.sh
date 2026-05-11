#!/bin/bash
set -e

export LD_LIBRARY_PATH="/usr/lib64:/home/net/sh440529/FullCustom/Full_Customs_Final/final_project_full_with_libs/klayout_ruby/usr/lib64/klayout:$LD_LIBRARY_PATH"

DRC_RULE="./klayout/drc/sky130A_mr.drc"

/home/net/sh440529/FullCustom/Full_Customs_Final/final_project_full_with_libs/klayout_ruby/usr/bin/klayout \
    -b \
    -r "$DRC_RULE" \
    -rd input="./results/riscv_soc_merged.gds" \
    -rd top_cell="riscv_soc" \
    -rd report="klayout_drc_official.lyrdb" \
    -rd feol="false" \
    -rd beol="true" \
    -rd offgrid="false" \
    -rd seal="false" \
    2>&1 | tee results/klayout_drc.log
