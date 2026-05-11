# RISC-V SoC Physical Design Flow

## Overview
This project implements an RTL-to-GDSII physical design flow for a RISC-V SoC using Synopsys Design Compiler, Synopsys ICC2, and KLayout.

The flow includes RTL synthesis, gate-level netlist generation, floorplanning, SRAM macro integration, power planning, placement, clock tree synthesis, routing, timing analysis, and DRC verification.

## Tools Used
- Synopsys Design Compiler
- Synopsys ICC2
- KLayout
- SkyWater 130nm technology
- Verilog
- Tcl
- Python

## Physical Design Flow
1. RTL synthesis
2. Timing constraint setup
3. Floorplanning
4. SRAM macro placement
5. Power distribution network design
6. Placement optimization
7. Clock tree synthesis
8. Routing
9. Timing analysis
10. DRC verification

## Key Results
| Metric | Result |
|---|---|
| Synthesis WNS | 0 ns |
| Synthesis TNS | 0 ns |
| Routing DRC | 0 violations |
| Final Setup WNS | ~-0.48 ns |
| Cell Area | 2,951,037.89 |
| Total Power | 15.0674 mW |

## Main Challenges
- SRAM macro integration
- Physical library setup
- Macro placement
- Power/ground connectivity
- Timing closure
- Routing congestion
- DRC/LVS debugging

## Repository Notes
Large generated files such as GDS, SPEF, Synopsys databases, and technology libraries are excluded due to file size and licensing constraints.