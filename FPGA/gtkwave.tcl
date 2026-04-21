gtkwave::loadFile counter.fst
set nfacs [gtkwave::getNumFacs]
for {set i 0} {$i < $nfacs} {incr i} {
    gtkwave::addSignalsFromList [list [gtkwave::getFacName $i]]
}
gtkwave::/Time/Zoom/Zoom_Full
