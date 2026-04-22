# Waveform file is already passed via "gtkwave -f" in run_demo.sh.
# Auto-detect and add only top-level tb_counter signals to avoid duplicates.
set nfacs [gtkwave::getNumFacs]
set signal_list [list]

for {set i 0} {$i < $nfacs} {incr i} {
    set fac [gtkwave::getFacName $i]
    if {[regexp {^tb_counter\.(clk|rst_n|count(\[[0-9:]+\])?)$} $fac]} {
        lappend signal_list $fac
    }
}

puts "GTKWAVE TCL selected signals: $signal_list"
if {[llength $signal_list] == 0} {
    puts "GTKWAVE TCL warning: no matching tb_counter signals found, falling back to all facilities"
    for {set i 0} {$i < $nfacs} {incr i} {
        lappend signal_list [gtkwave::getFacName $i]
    }
}

gtkwave::addSignalsFromList $signal_list
gtkwave::/Time/Zoom/Zoom_Full
