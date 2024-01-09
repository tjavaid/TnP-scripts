# Instructions for for setting up and running for low pT ID efficiency measurement using 2022 data
After logging into the ```ihep (lxslc7.ihep.ac.cn``` machine account, following steps can be followed:
## 1. Setup 
```
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_10_2_5
cd CMSSW_10_2_5/src
cmsenv
git clone -b CMS-China-WC2-2022data https://github.com/tjavaid/TnP-scripts.git
git clone -b 102x https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.2.0
scramv1 b clean; scramv1 b
```
## 2. Running the fits
First of all navigate to the directory containing the tag and probe scripts:
```
cd $CMSSW_BASE/src/TnP-scripts
```
The macro used to produce fits for passing and failing probes is ```tnpEfficiency.py``` which can be triggered using the bash script ```runTnP_MuPOG_jpsi_2022.sh``` with necessary arguments about ```era (i.e. 2022BCD or 2022EFG)```, ```mode (i.e. nominal or syst or all) ``` and ```ID type(i.e. loose, medium or tight)```. For example, the nominal or default fits can be triggered for 2022BCD and Loose ID using the command line:
```
sh runTnP_MuPOG_jpsi_2022.sh 2022BCD nominal loose
```
Similary, to run the fits for nominal and as well as for other alternate choices (used for systematics) can be run using:
```
sh runTnP_MuPOG_jpsi_2022.sh 2022BCD all loose
```
## 2. Producing the final efficiency and scale factor plots with systematics included
The macro used for this step is ```tnpHarvest.py``` which can be triggered using the bash script ```harvestTnP_MuPOG_ID_2022.sh``` by providing arguments for ```era (i.e. 2022BCD or 2022EFG)``` and ```ID type(i.e. loose, medium or tight)```. For example for 2022BCD and Loose ID it is run as:
```
sh harvestTnP_MuPOG_ID_2022.sh 2022BCD loose
```


