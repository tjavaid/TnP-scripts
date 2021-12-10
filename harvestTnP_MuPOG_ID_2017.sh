#!/bin/bash

P="test"
IN="mupog_RecoId"
MEAS="mu_Loose"                         ##can be the type measurement  ............................OK
for sig in JDGauss JCB; do
    for bkg in bern4 expo; do
        for salt in JDGauss JCB; do
            if [[ "$salt" != "$sig" ]]; then
            for balt in  bern4 expo ; do
                if [[ "$balt" != "$bkg" ]]; then
		if [[ "$1" != "" ]]; then MEAS="$*"; fi
		for M in $MEAS; do
		    case $M in
			mu_Loose) MODS=" -s "${sig}" -b "${bkg}"  --balt "${balt}" --salt "${salt}"  ";   #
			mu_Loose) MODS=" -s "${sig}" -b "${bkg}"  --balt "${balt}" --salt "${salt}" --alt massExtended --alt massReduced --alt binsExtended --alt binsReduced ";   #MCT, expo with no voigt, bern3 as alternate
			OUT="$IN/${M}_2017_harvest_${sig}_${bkg}_${salt}_${balt}_mupogSysts"
                        TIT='Muon Id efficiency' ;;
    		    esac;
                    OPTS=" --doRatio --pdir ${P}/$OUT --idir ${P}/$IN  --rrange 0.97 1.01  --yrange 0.9 1.01 "; XTIT="p_{T} (GeV)"
		    for BE in barrel endcap; do
		        python tnpHarvest.py -N ${M}_${BE} $OPTS $MODS --ytitle "$TIT" --xtit "$XTIT"
		    done
		    python tnpHarvest.py -N ${M}_pt7 $OPTS $MODS --ytitle "$TIT" --xtit "#eta"
		    python tnpHarvest.py -N ${M}_pt7_vtx $OPTS $MODS --ytitle "$TIT" --xtit "N(vertices)"
		done
		fi;
done;
fi;
done;
done
done
