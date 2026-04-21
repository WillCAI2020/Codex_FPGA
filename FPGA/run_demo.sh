#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-out}"
mkdir -p "$OUT_DIR"

iverilog -g2012 -o "$OUT_DIR/simv" tb_counter.v counter.v
vvp "$OUT_DIR/simv" | tee "$OUT_DIR/sim.log"
# tb_counter.v writes counter.vcd in current working directory
mv -f counter.vcd "$OUT_DIR/counter.vcd"
vcd2fst "$OUT_DIR/counter.vcd" "$OUT_DIR/counter.fst"

if command -v xvfb-run >/dev/null 2>&1; then
  xvfb-run -a bash -lc "
    gtkwave -f '$OUT_DIR/counter.fst' -S gtkwave.tcl > '$OUT_DIR/gtkwave.log' 2>&1 &
    pid=\$!
    sleep 4
    xwd -root -silent -out '$OUT_DIR/gtkwave.xwd'
    kill \$pid || true
    wait \$pid || true
  "
  convert "$OUT_DIR/gtkwave.xwd" "$OUT_DIR/waveform.png"
else
  echo "xvfb-run not found, skipping gtkwave image export"
fi

echo "Artifacts generated under: $OUT_DIR"
