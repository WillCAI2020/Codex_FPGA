gtkwave::loadFile counter.fst

# Avoid duplicate aliases by selecting only top-level signals of interest.
set signal_list [list \
    "tb_counter.clk" \
    "tb_counter.rst_n" \
    "tb_counter.count[3:0]" \
]
gtkwave::addSignalsFromList $signal_list

gtkwave::/Time/Zoom/Zoom_Full
