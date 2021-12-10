#!/bin/bash

#case $HOSTNAME in
#cmsco01*) P=/data1/gpetrucc/MUPOG_TnP_76X/ ;;
#*) exit 1; P=root://eoscms//eos/cms/store/group/phys_muon/TagAndProbe/76XtreeProduction/v41/ ;;
#esac;

#PDIR="../plotting/plots/76X_220116/zTnP/"
#PDIR="../plotting/plots/94X_020418/zTnP/"
PDIR="test/"
##JOB="mupog_v2_jpsi"

JOB="mupog_RecoId"                       ## FULL DATA & MC
#JOB="mupog_RecoId_MCT"
##JOB="mupog_RecoId_2"   ##excluded JGauss among SMOD

XBINS="[3,4,5,6,7,8,10,12,15,20]"

EBINS="[-2.4,-2.1,-1.6,-1.2,-0.9,-0.6,-0.3,-0.2,0.2,0.3,0.6,0.9,1.2,1.6,2.1,2.4]"
VBINS="[0.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,17.5,20.5]"

#MC=$P/tnpJPsi_MC_JPsiPt8_full.root
#MC='/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/92X-v2_TrkIter/MC/TnPTree_DYLL_M50_Madgraph.root'
#MC='/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/MC/TnPTreeJPsi_94X_JpsiToMuMu_Pythia8.root'

#MC='root://eoscms.cern.ch//eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/MC/TnPTreeJPsi_94X_JpsiToMuMu_Pythia8.root'
#MC='/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/MC/TnPTree_94X_DYJetsToLL_M50_Madgraph.root'
##MC='/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/MC/TnPTreeJPsi_94X_JpsiToMuMu_Pythia8.root'
#DATA=$P/tnpJPsi_Data_Run2015D.root

##DATA='/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/RunB/TnPTreeJPsi_17Nov2017_Charmonium_Run2017Bv1_Full_GoldenJSON_BUGFIX.root'

##below list is to be added to above DATA.
#list=("C D E F")
#DATA=$(for i in $list; do echo /eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/Run$i/TnPTreeJPsi_17Nov2017_Charmonium_Run2017$i\v1_Full_GoldenJSON.root; done)




####################################*****AHMAD******#######################
#DATA=""
#for i in B C D E F
# do 
# if[ ${i} == "B" ]
# then DATA=${DATA}""$(echo /eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/Run$i/TnPTreeJPsi_17Nov2017_Charmonium_Run2017$i\v1_Full_GoldenJSON_BUGFIX.root) 
# DATA=${DATA}""$( echo /eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/Run$i/TnPTreeJPsi_17Nov2017_Charmonium_Run2017$i\v1_Full_GoldenJSON.root)
#fi 
# done
###########################################################################
#MC='/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/MC/TnPTreeJPsi_94X_JpsiToMuMu_Pythia8.root'
MC='/eos/cms/store/group/phys_muon/TagAndProbe/HZZ4L_2017/MC/TnPTreeJPsi_94X_JpsiToMuMu_Pythia8_skimmed_weightAdded.root'
DATA='/eos/cms/store/group/phys_muon/TagAndProbe/HZZ4L_2017/Data/TnPTreeJPsi_17Nov2017_Charmonium_Run2017B2F_skimmed.root'

#DATA='/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/RunB/TnPTreeJPsi_17Nov2017_Charmonium_Run2017Bv1_Full_GoldenJSON_BUGFIX.root'
#/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/RunC/TnPTreeJPsi_17Nov2017_Charmonium_Run2017Cv1_Full_GoldenJSON.root
#/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/RunD/TnPTreeJPsi_17Nov2017_Charmonium_Run2017Dv1_Full_GoldenJSON.root
#/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/RunE/TnPTreeJPsi_17Nov2017_Charmonium_Run2017Ev1_Full_GoldenJSON.root
#/eos/cms/store/group/phys_muon/TagAndProbe/Run2017/94X/JPsi/RunF/TnPTreeJPsi_17Nov2017_Charmonium_Run2017Fv1_Full_GoldenJSON.root'

echo "$DATA"
echo "$MC"

PDS="$DATA --refmc $MC"

OPTS=" --doRatio  --pdir $PDIR/$JOB -j 5 --mcw weight"
OPTS="$OPTS -t tpTree/fitter_tree  --mc-cut 1 --mc-mass mass   "

if [[ "$1" != "" ]]; then SEL=$1; OPTS="$OPTS --reqname $1 "; shift; fi
if [[ "$1" != "" ]]; then OPTS="$OPTS $* "; shift; fi
MASS="  -m mass 80,2.85,3.34"
CDEN=" tag_Mu7p5_Track2_Jpsi_MU && pair_drM1 > 0.5 "


#for ID in Loose Reco LooseIdOnly; do
for ID in Loose ; do

  if [[ "$SEL" != "" ]] && echo $SEL | grep -q -v $ID; then continue; fi
  NUM="$ID"        #??
  if [[ "$ID" == "Reco" ]]; then   NUM="(Glb || TM)"; fi

  if [[ "$ID" == "LooseIdOnly" ]]; then NUM="Loose"; CDEN="$CDEN && (Glb || TM)"; fi

#  for BMOD in bern1 bern2 bern5; do #bern3 bern4 expo; do #till 12.07.2018
#  for BMOD in expo bern5; do
echo $NUM
echo $CDEN
  for BMOD in expo bern3; do
    if [[ "$SEL" != "" ]] && echo $SEL | grep -q "_" && echo $SEL | grep -q -v $BMOD; then continue; fi
#    for SMOD in  JDGauss JCB; do  # till 12.07.2018
#    for SMOD in  MCTDCB; do    # adding more signal lineshape tempplates
##    for SMOD in  JDGauss JGauss  JCB; do
##    for SMOD in  MCT JDGauss JGauss  JCB; do ## MC template
    for SMOD in  JDGauss JCB; do
        if [[ "$SEL" != "" ]] && echo $SEL | grep -q "_" && echo $SEL | grep -q -v $BMOD; then continue; fi
        DEN="$CDEN"; POST=""
        python tnpEfficiency.py $PDS -d "abs(eta)<1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS --xtitle "p_{T} (GeV)" ;
        python tnpEfficiency.py $PDS -d "abs(eta)>1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS --xtitle "p_{T} (GeV)";
        python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7   -b $BMOD -s $SMOD $MASS  --xtitle "#eta";
        python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var tag_nVertices $VBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7_vtx   -b $BMOD -s $SMOD $MASS --xtitle "N(vertices)";
   
##     if [[ "$SMOD" == "JDGauss" && "$BMOD" == "bern3" ]]; then
 ##    if [[ "$SMOD" == "MCT" && "$BMOD" == "bern3" ]]; then 
#     if [[ "$SMOD" == "JDGauss" && "$BMOD" == "expo" ]]; then
#     if [[ "$SMOD" == "JCB" && "$BMOD" == "expo" ]]; then


#####  adding alternates



#     if [[ ("$SMOD" == "JDGauss" || "$SMOD" == "JCB") && ("$BMOD" == "expo" || "$BMOD" == "bern5" ) ]]; then
#            MASS2=" -m mass 80,2.90,3.29"; POST="_massReduced"  # with reduced mass range (default is 80,2.85,3.34)
#            python tnpEfficiency.py $PDS -d "abs(eta)<1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)" ;
#            python tnpEfficiency.py $PDS -d "abs(eta)>1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7   -b $BMOD -s $SMOD $MASS2  --xtitle "#eta";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var tag_nVertices $VBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7_vtx   -b $BMOD -s $SMOD $MASS2 --xtitle "N(vertices)";
#
#            MASS2=" -m mass 80,2.80,3.39"; POST="_massExtended"  # with extended mass range (default is 80,2.85,3.34)
#            python tnpEfficiency.py $PDS -d "abs(eta)<1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)" ;
#            python tnpEfficiency.py $PDS -d "abs(eta)>1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7   -b $BMOD -s $SMOD $MASS2  --xtitle "#eta";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var tag_nVertices $VBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7_vtx   -b $BMOD -s $SMOD $MASS2 --xtitle "N(vertices)";
#
#            MASS2=" -m mass 70,2.85,3.34"; POST="_binsReduced"  # with reduced no. of bins in mass range (default is 80,2.85,3.34)
#            python tnpEfficiency.py $PDS -d "abs(eta)<1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)" ;
#            python tnpEfficiency.py $PDS -d "abs(eta)>1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7   -b $BMOD -s $SMOD $MASS2  --xtitle "#eta";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var tag_nVertices $VBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7_vtx   -b $BMOD -s $SMOD $MASS2 --xtitle "N(vertices)";
#
#            MASS2=" -m mass 90,2.85,3.34"; POST="_binsExtended"  # with extended no. of bins in mass range (default is 80,2.85,3.34)
#            python tnpEfficiency.py $PDS -d "abs(eta)<1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)" ;
#            python tnpEfficiency.py $PDS -d "abs(eta)>1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS2 --xtitle "p_{T} (GeV)";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7   -b $BMOD -s $SMOD $MASS2  --xtitle "#eta";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var tag_nVertices $VBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7_vtx   -b $BMOD -s $SMOD $MASS2 --xtitle "N(vertices)";
#
#
#            DEN="$CDEN && SIP < 4"; POST="_sip4"
#            python tnpEfficiency.py $PDS -d "abs(eta)<1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS --xtitle "p_{T} (GeV)" ;
#            python tnpEfficiency.py $PDS -d "abs(eta)>1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS --xtitle "p_{T} (GeV)";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7   -b $BMOD -s $SMOD $MASS  --xtitle "#eta";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var tag_nVertices $VBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7_vtx   -b $BMOD -s $SMOD $MASS --xtitle "N(vertices)";
#            
#            DEN="$CDEN && pair_distM2 > 200 && pair_dphiVtxTimesQ < 0"; POST="_sep"
#            python tnpEfficiency.py $PDS -d "abs(eta)<1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_barrel -b $BMOD -s $SMOD $MASS --xtitle "p_{T} (GeV)" ;
#            python tnpEfficiency.py $PDS -d "abs(eta)>1.2 && $DEN" -n "$NUM" $OPTS --x-var pt $XBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_endcap -b $BMOD -s $SMOD $MASS --xtitle "p_{T} (GeV)";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var eta $EBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7   -b $BMOD -s $SMOD $MASS  --xtitle "#eta";
#            python tnpEfficiency.py $PDS -d "pt > 7 && $DEN" -n "$NUM" $OPTS --x-var tag_nVertices $VBINS -N mu_${SMOD}_${BMOD}${POST}_${ID}_pt7_vtx   -b $BMOD -s $SMOD $MASS --xtitle "N(vertices)";
##        fi;
    done    
  done
done
