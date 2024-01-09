#!/bin/bash

P=$1"_TnP"
if [[ $1 == "" ]]; then echo "please provide the era to be processed (2022BCD or 2022EFG). Thanks!"; exit; fi
IN="mupog_RecoId"

declare -A ids
ids["loose"]="probe_CutBasedIdLoose"
ids["medium"]="probe_CutBasedIdMedium"
ids["tight"]="probe_CutBasedIdTight"

id=${ids[$2]}
echo "ID is : " $id

#MEAS="mu_probe_CutBasedIdLoose"                         # type of measurement
MEAS="mu_"$id

for sig in JGauss JCB; do
    for bkg in bern3 expo; do
        for salt in JGauss JCB; do
            if [[ "$salt" != "$sig" ]]; then
            for balt in bern3 expo ; do
                if [[ "$balt" != "$bkg" ]]; then
		for M in $MEAS; do
		    case $M in
			mu_$id) MODS=" -s "${sig}" -b "${bkg}"  --balt "${balt}" --salt "${salt}"  ";   
			#mu_$id) MODS=" -s "${sig}" -b "${bkg}"  --balt "${balt}" --salt "${salt}" --alt massExtended --alt massReduced --alt binsExtended --alt binsReduced ";   
			OUT="$IN/${M}_$1_harvest_${sig}_${bkg}_${salt}_${balt}_mupogSysts"
                        TIT='Muon Id efficiency' ;;
    		    esac;
                    OPTS=" --doRatio --pdir ${P}/$OUT --idir ${P}/$IN  --rrange 0.97 1.01  --yrange 0.9 1.01 "; XTIT="p_{T} (GeV)"
		    for BE in barrel endcap ; do
		        python tnpHarvest.py -N ${M}_${BE} $OPTS $MODS --ytitle "$TIT" --xtit "$XTIT"
		    done
		    python tnpHarvest.py -N ${M}_pt2 $OPTS $MODS --ytitle "$TIT" --xtit "#eta"
		done
		fi;
done;
fi;
done;
done
done

