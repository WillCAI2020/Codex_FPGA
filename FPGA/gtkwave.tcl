# Waveform file is already passed via "gtkwave -f" in run_demo.sh.
# Use brace-quoted signal names so [3:0] is not interpreted by Tcl.
set signal_list [list \
    {tb_counter.clk} \
    {tb_counter.rst_n} \
    {tb_counter.count[3:0]} \
]
gtkwave::addSignalsFromList $signal_list

gtkwave::/Time/Zoom/Zoom_Full
