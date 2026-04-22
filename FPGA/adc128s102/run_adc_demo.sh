#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-out}"
mkdir -p "$OUT_DIR"

iverilog -g2012 -o "$OUT_DIR/adc_simv" \
  tb_b128s102rh_core.v b128s102rh_core.v adc128s102_model.v

vvp "$OUT_DIR/adc_simv" | tee "$OUT_DIR/adc_sim.log"
mv -f adc128s102.vcd "$OUT_DIR/adc128s102.vcd"
vcd2fst "$OUT_DIR/adc128s102.vcd" "$OUT_DIR/adc128s102.fst"

echo "ADC demo artifacts generated under: $OUT_DIR"
