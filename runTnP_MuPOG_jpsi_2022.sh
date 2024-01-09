#!/bin/bash

#PDIR="test/"
PDIR=$1"_TnP"
if [[ $1 != "" ]]; then echo "PDIR:", $PDIR; fi
JOB="mupog_RecoId" 

#XBINS="[3,4,5,6,7,8,9,10,30]" # POG
XBINS="[3,4.5,6,7.5,9,12,15,20]" # defining bins in pT of muons (used for barrel and endcap plots)

EBINS="[-2.4,-2.1,-1.6,-1.2,-0.9,-0.3,-0.2,0.2,0.3,0.9,1.2,1.6,2.1,2.4]" # defining bins in eta of muons (inclusive for pT of muons)
#EBINS="[0,0.3,0.55,0.8,1.1,1.4,1.85,2.4]"   #    arbitrary, HIG-21-009
VBINS="[0.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,17.5,20.5]" # bins for no. of vetices


if [[ $1 != "" ]]; then echo "era being processed is:       ", $1; fi
###########################################################################
# Data and MC samples used for the studies
if [[ "$1" == "2022BCD" ]]; then MC='/publicfs/cms/data/hzz/jtahir/WC2/Run3/Run2022/haddOut_JPsi_pythia8_skimmed_weightAdded.root'; 
DATA='/publicfs/cms/data/hzz/jtahir/WC2/Run3/Run2022/haddOut_RunB_skimmed.root
/publicfs/cms/data/hzz/jtahir/WC2/Run3/Run2022/haddOut_RunC_skimmed.root
/publicfs/cms/data/hzz/jtahir/WC2/Run3/Run2022/haddOut_RunD_skimmed.root
';
elif [[ "$1" == "2022EFG" ]]; then
MC='/publicfs/cms/data/hzz/jtahir/WC2/Run3/Run2022_EE/haddOut_JPsi_pythia8_skimmed_weightAdded.root'
DATA='/publicfs/cms/data/hzz/jtahir/WC2/Run3/Run2022_EE/haddOut_RunE_skimmed.root
/publicfs/cms/data/hzz/jtahir/WC2/Run3/Run2022_EE/haddOut_RunF_skimmed.root
/publicfs/cms/data/hzz/jtahir/WC2/Run3/Run2022_EE/haddOut_RunG_skimmed.root
';
else echo "please enter the era to be processed. Thanks!"; exit
fi

if [[ $2 == "" ]]; then echo "please specify the mode (nominal, syst or all)! "; exit
fi
echo "$DATA"
echo "$MC"

PDS="$DATA --refmc $MC"

OPTS=" --doRatio  --pdir $PDIR/$JOB -j 5 --mcw weight " #--mcw genWeight
OPTS="$OPTS -t muon/Events  --mc-cut 1 --mc-mass pair_mass   "

MASS="  -m pair_mass 40,2.9,3.3" # the default dimuon invariant mass window and no. of data points i.e. 40

echo $CDEN

# tag muon selections (matched to a trigger object from a single muon trigger)
CDEN="tag_pt > 8 && abs(tag_eta) < 2.4 && tag_isTight==1 && (tag_HLT_Mu8_v==1 || tag_HLT_Mu15_v==1 || tag_HLT_Mu17_v==1 || tag_HLT_Mu19_v==1 || tag_HLT_Mu20_v==1 || tag_HLT_IsoMu24_v==1)"

# probe muon selections
CDEN="$CDEN && probe_isTracker==1 && probe_pt > 2 && abs(probe_dz) < 0.5"

# pair conditions
CDEN="$CDEN && pair_probeMultiplicity==1 && pair_drM1>= 0.3" # pair_probeMultiplicity -> pairs whose probe muon is associated to only one tag muon, pair_drM1-> dR between tag and probe muons


#for ID in probe_isLoose ; do
for ID in probe_CutBasedIdLoose; do
 # if [[ "$SEL" != "" ]] && echo $SEL | grep -q -v $ID; then continue; fi
  NUM="$ID"        
  if [[ "$ID" == "Reco" ]]; then   NUM="(Glb || TM)"; fi

  if [[ "$ID" == "LooseIdOnly" ]]; then NUM="Loose"; CDEN="$CDEN && (Glb || TM)"; fi

echo $NUM
echo $CDEN
  #for BMOD in expo  ; do  # other alternate models are bern4, bern5, bern6, bern7, expo , etc....
  for BMOD in expo bern3 ; do  # other alternate models are bern4, bern5, bern6, bern7, expo , etc....
#    for SMOD in JGauss ; do  # other alternate model is  JDGauss JCB
    for SMOD in JCB JGauss; do  # 
	DEN="$CDEN";
	if [ "$2" == "nominal" ] || [ "$2" == "all" ]; then # to execute the nominal part 
	echo "running fits for the nominal part"
        POST="";
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>0 && abs(probe_eta)<=1.2 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>1.2 && abs(probe_eta)<=2.4 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "probe_pt > 2 && $DEN" -n "$NUM" $OPTS --x-var probe_eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt2   -b $BMOD -s $SMOD $MASS  --xtitle "#eta" --yrange 0.8 1.1; 
	fi
######  adding more  alternate choices ((than the signal and background PDFs)) for systematics purposes
	if [ "$2" == "syst" ] || [ "$2" == "all" ]; then 
	echo "running fits for the syst. part";
        MASS2=" -m pair_mass 20,2.95,3.25"; POST="_massReduced";
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>0 && abs(probe_eta)<=1.2 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>1.2 && abs(probe_eta)<=2.4 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "probe_pt > 2 && $DEN" -n "$NUM" $OPTS --x-var probe_eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt2   -b $BMOD -s $SMOD $MASS2  --xtitle "#eta" ;
#
        MASS2=" -m pair_mass 20,2.85,3.35"; POST="_massExtended"  # with extended mass range (default is 20,2.9,3.3)
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>0 && abs(probe_eta)<=1.2 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>1.2 && abs(probe_eta)<=2.4 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "probe_pt > 2 && $DEN" -n "$NUM" $OPTS --x-var probe_eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt2   -b $BMOD -s $SMOD $MASS2  --xtitle "#eta" ;
#
        MASS2=" -m pair_mass 15,2.9,3.3"; POST="_binsReduced"  # with reduced bins in mass range (default is 20,2.9,3.3)
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>0 && abs(probe_eta)<=1.2 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>1.2 && abs(probe_eta)<=2.4 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "probe_pt > 2 && $DEN" -n "$NUM" $OPTS --x-var probe_eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt2   -b $BMOD -s $SMOD $MASS2  --xtitle "#eta" ;
#
        MASS2=" -m pair_mass 30,2.9,3.3"; POST="_binsExtended"  # with extended bins in mass range (default is 20,2.9,3.3)
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>0 && abs(probe_eta)<=1.2 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "abs(probe_eta)>1.2 && abs(probe_eta)<=2.4 && $DEN" -n "$NUM" $OPTS --x-var probe_pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "probe_pt > 2 && $DEN" -n "$NUM" $OPTS --x-var probe_eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt2   -b $BMOD -s $SMOD $MASS2  --xtitle "#eta" ;
	fi; 
    done    
  done
done
