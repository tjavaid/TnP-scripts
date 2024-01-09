#!/bin/bash

P=$1"_TnP"
if [[ $1 == "" ]]; then echo "please provide the era to be processed (2022BCD or 2022EFG). Thanks!"; exit; fi
echo "P:   ", $P
IN="mupog_RecoId"
MEAS="mu_probe_CutBasedIdLoose"                         # type of measurement

for sig in JGauss JCB; do
    for bkg in bern3 expo; do
        for salt in JGauss JCB; do
            if [[ "$salt" != "$sig" ]]; then
            for balt in bern3 expo ; do
                if [[ "$balt" != "$bkg" ]]; then
		for M in $MEAS; do
		    case $M in
			#mu_probe_CutBasedIdLoose) MODS=" -s "${sig}" -b "${bkg}"  --balt "${balt}" --salt "${salt}"  ";   #
			mu_probe_CutBasedIdLoose) MODS=" -s "${sig}" -b "${bkg}"  --balt "${balt}" --salt "${salt}" --alt massExtended --alt massReduced --alt binsExtended --alt binsReduced ";   
			OUT="$IN/${M}_$1_harvest_${sig}_${bkg}_${salt}_${balt}_mupogSysts"
                        TIT='Muon Id efficiency' ;;
    		    esac;
                    #OPTS=" --doRatio --pdir ${P}/$OUT --idir ${P}/$IN  --rrange 0.97 1.01  --yrange 0.9 1.01 "; XTIT="p_{T} (GeV)"
                    OPTS=" --doRatio --pdir /eos/user/t/tjavaid/www/${P}/$OUT --idir ${P}/$IN  --rrange 0.97 1.01  --yrange 0.9 1.01 "; XTIT="p_{T} (GeV)"
		    for BE in barrel endcap ; do
		        python tnpHarvest.py -N ${M}_${BE} $OPTS $MODS --ytitle "$TIT" --xtit "$XTIT"
		    done
		    python tnpHarvest.py -N ${M}_pt2 $OPTS $MODS --ytitle "$TIT" --xtit "#eta"
#		    python tnpHarvest.py -N ${M}_pt7_vtx $OPTS $MODS --ytitle "$TIT" --xtit "N(vertices)"
		done
		fi;
done;
fi;
done;
done
done

