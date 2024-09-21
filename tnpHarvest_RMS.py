import ROOT, os
from array import array
from glob import glob
from math import sqrt, hypot, log


def hypsub(all,stat):
    return sqrt(max(all*all-stat*stat,0))

def uniformAxis_(expr):
    (bins,xmin,xmax) = map(float,expr.split(","))
    dx = (xmax-xmin)/int(bins)
    return [ (xmin + dx*i) for i in xrange(0,int(bins)+1) ]

def makeTGraph(effs):
    ret = ROOT.TGraphAsymmErrors(len(effs))
    for i,(x,xl,xh,eff,effl,effh) in enumerate(effs):
        ret.SetPoint(i, x, eff)
        ret.SetPointError(i, -xl,xh, -effl,effh)
    return ret

def makeRatios(data):
    numeff = data["data"]
    deneff = data["ref"]
    xn = numeff.GetX() # data eff.
    print "xn:      ", xn
    yn = numeff.GetY()
    xd = deneff.GetX()
    yd = deneff.GetY() # MC eff.
    ratio = ROOT.TGraphAsymmErrors(numeff.GetN())
    ratio_rms = ROOT.TGraphAsymmErrors(numeff.GetN())
    rater = ROOT.TGraphAsymmErrors(numeff.GetN())
    unity = ROOT.TGraphAsymmErrors(numeff.GetN())
    #print "numeff.GetN():  ", numeff.GetN()
    for i in xrange(numeff.GetN()): # loop over data eff. bins.
        found = False
        for i2 in xrange(deneff.GetN()): # loop over MC eff. bins
            if abs(xn[i]-xd[i2]) < 1e-4: 
                found = True; break
        if yd[i2] <= 0 or not found:
            unity.SetPoint(i , xn[i ], -99)
            ratio.SetPoint(i , xn[i ], -99)
            ratio_rms.SetPoint(i , xn[i ], -99)
            rater.SetPoint(i , xn[i ], -99)
        else:
	    #print "xn[i ]", xn[i ], "yn[i ]", yn[i ], "yd[i2]", yd[i2], ",, yn[i ]/yd[i2]", yn[i ]/yd[i2]
            ratio.SetPoint(i , xn[i ], yn[i ]/yd[i2])
            ratio_rms.SetPoint(i , xn[i ], yn[i ]/yd[i2])
            rater.SetPoint(i , xn[i ], yn[i ]/yd[i2])
            unity.SetPoint(i , xn[i ], 1.0)
            ratio.SetPointError(i , numeff.GetErrorXlow(i ), numeff.GetErrorXhigh(i ), numeff.GetErrorYlow(i )/yd[i2], numeff.GetErrorYhigh(i )/yd[i2]) # this one has ratio with only data stat. uncertainties  ?
            unity.SetPointError(i , deneff.GetErrorXlow(i2), deneff.GetErrorXhigh(i2), deneff.GetErrorYlow(i2)/yd[i2], deneff.GetErrorYhigh(i2)/yd[i2]) # assigned from MC stat unc. ?
            rater.SetPointError(i , numeff.GetErrorXlow(i ), numeff.GetErrorXhigh(i ),
                                    hypot(ratio.GetErrorYlow(i),unity.GetErrorYhigh(i)),
                                    hypot(ratio.GetErrorYhigh(i),unity.GetErrorYlow(i))) # has uncertainties from data and MC both......       why opposite ? investigate, unity ?
	    print "i::", i
	    print "xn[i ]", xn[i ], "yn[i ]", yn[i ], "yd[i2]", yd[i2], ",, yn[i ]/yd[i2]", yn[i ]/yd[i2]
	    print "data : numeff.GetErrorYlow(i ): ", numeff.GetErrorYlow(i )
	    print "data: numeff.GetErrorYhigh(i ): ", numeff.GetErrorYhigh(i )
	    print "MC : deneff.GetErrorYlow(i ): ", deneff.GetErrorYlow(i )
	    print "MC: deneff.GetErrorYhigh(i ): ", deneff.GetErrorYhigh(i )
	    print "ratio:    ratio.GetErrorYlow(i): ", ratio.GetErrorYlow(i)
	    print "ratio:    ratio.GetErrorYhigh(i): ", ratio.GetErrorYhigh(i)
	    print "ratioErr:    rater.GetErrorYlow(i): ", rater.GetErrorYlow(i)
	    print "ratioErr:    rater.GetErrorYhigh(i): ", rater.GetErrorYhigh(i)
	    print " testing"
    data["ratio"] = ratio
   # data["ratio_rms"] = ratio_rms
    data["unity"] = unity
    data["ratioErr"] = rater

def styleCommon(graph,options):
    graph.GetYaxis().SetRangeUser(options.yrange[0], options.yrange[1])
    graph.GetYaxis().SetDecimals(True)
    if options.xtitle: graph.GetXaxis().SetTitle(options.xtitle)
    if options.ytitle: graph.GetYaxis().SetTitle(options.ytitle)

def styleAsData(graph,options):
    styleCommon(graph,options)
    graph.SetMarkerStyle(20)
    graph.SetLineWidth(2)
    graph.SetLineColor(ROOT.kBlack)
    graph.SetMarkerColor(ROOT.kBlack)
    gsyst = getattr(graph, 'syst', None)
    if gsyst:
        styleCommon(gsyst,options)
        gsyst.SetMarkerStyle(0)
        gsyst.SetLineWidth(4)
        gsyst.SetLineColor(ROOT.kRed+0)
        gsyst.SetMarkerColor(ROOT.kRed+0)

def styleAsRef(graph,options):
    styleCommon(graph,options)
    graph.SetMarkerStyle(20)
    graph.SetFillColor(ROOT.kAzure+10)
    gsyst = getattr(graph, 'syst', None)
    if gsyst:
        styleCommon(gsyst,options)
        gsyst.SetMarkerStyle(20)
        gsyst.SetFillColor(ROOT.kViolet+6)

def stackEfficiencies(base,ref,options):
    styleAsData(base,options)
    styleAsRef(ref,options)
    ref.Draw("AE2");
    if hasattr(ref,"syst"):
        ref.syst.Draw("E2 SAME");
        ref.Draw("E2 SAME");
    if hasattr(base,"syst"):
        base.syst.Draw("PZ SAME");
    base.Draw("PZ SAME");

def plotRatio(effs,ratio,options):
    for e in effs:
        e.GetXaxis().SetLabelOffset(999) ## send them away
        e.GetXaxis().SetTitleOffset(999) ## in outer space
        e.GetYaxis().SetLabelSize(0.05)
    ratiosyst = getattr(ratio, 'syst', None)
    allratios = [ratio]
    styleAsData(ratio,options)
    if ratiosyst: 
        allratios += [ratiosyst, ratio.systOnly]
        ymax = max(ratiosyst.GetY()[i]+ratiosyst.GetErrorYhigh(i) for i in xrange(ratiosyst.GetN()))
        ymin = min(ratiosyst.GetY()[i]-ratiosyst.GetErrorYlow(i)  for i in xrange(ratiosyst.GetN()))
    else:
        ymax = max(ratio.GetY()[i]+ratio.GetErrorYhigh(i) for i in xrange(ratio.GetN()))
        ymin = min(ratio.GetY()[i]-ratio.GetErrorYlow(i)  for i in xrange(ratio.GetN()))
    for r in allratios:
        r.GetYaxis().SetRangeUser(1+1.3*(min(0.99,ymin)-1),1+1.3*(max(1.01,ymax)-1));
        r.GetXaxis().SetTitleSize(0.14)
        r.GetYaxis().SetTitleSize(0.14)
        r.GetXaxis().SetLabelSize(0.11)
        r.GetYaxis().SetLabelSize(0.11)
        r.GetYaxis().SetNdivisions(505)
        r.GetYaxis().SetTitle("ratio")
        r.GetYaxis().SetTitleOffset(0.52);
    ratio.Draw("APZ")
    if options.rrange: 
        ratio.GetYaxis().SetRangeUser(options.rrange[0],options.rrange[1]);
    if ratiosyst:
        styleAsRef(ratiosyst,options)
        ratiosyst.SetFillColor(ROOT.kViolet+6)
        ratiosyst.Draw("E2 SAME")
        styleAsRef(ratio.systOnly,options)
        ratio.systOnly.SetFillColor(ROOT.kOrange-3)
        ratio.systOnly.Draw("E2 SAME")
    line = ROOT.TLine(ratio.GetXaxis().GetXmin(),1,ratio.GetXaxis().GetXmax(),1)
    line.SetLineWidth(2);
    line.SetLineColor(ROOT.kGray+2);
    line.SetLineStyle(2);
    line.DrawLine(ratio.GetXaxis().GetXmin(),1,ratio.GetXaxis().GetXmax(),1)
    ratio.Draw("PZ SAME")

def plotEffs(name,effs,ratio,options):
    c1 = ROOT.TCanvas("c1", "c1", 600, (750 if options.doRatio else 600))
    c1.Draw()
    p1, p2 = c1, None # high and low panes
    # set borders, if necessary create subpads
    if len(effs) > 1 and options.doRatio:
        c1.SetWindowSize(600 + (600 - c1.GetWw()), (750 + (750 - c1.GetWh())));
        #p1 = ROOT.TPad("pad1","pad1",0,0.31,1,1);
        p1 = ROOT.TPad("pad1","pad1",0,0.325,1,1);  # TJ
        p1.SetBottomMargin(0);
        p1.Draw();
        p2 = ROOT.TPad("pad2","pad2",0,0,1,0.31);
        p2.SetTopMargin(0);
        p2.SetBottomMargin(0.3);
        p2.SetFillStyle(0);
        p2.Draw();
        p1.cd();
    else:
        c1.SetWindowSize(600 + (600 - c1.GetWw()), 600 + (600 - c1.GetWh()));
    if len(effs) == 2:
        stackEfficiencies(effs[0],effs[1],options)
    else:
        styleAsData(effs[0],options)
        effs[0].Draw("AP")
    text = []
    if len(effs) > 1 and options.doRatio:
        p2.cd()
        plotRatio(effs,ratio,options) # ratio tgraph has already combined systematics for all sources
    #for ext in "pdf","png":
    for ext in "pdf","png","C":
        c1.Print("%s/%s.%s" % (options.printDir, name, ext))
    #print "testin:  ", TGraphByX(ratio.syst)
    if len(effs) == 2:
        dump = open("%s/%s.%s" % (options.printDir, name, "txt"), "w")
        #dump.write(" xmin   xmax     data[%] uncertainty  ref[%] uncertainty   scalef    (+/- stat)       (+/- syst)     scalef    (+/- tot)   \n")
        dump.write(" xmin   xmax     data[%] uncert.  MC[%] uncert.      SF      (-/+ stat)        (-/+ syst)           SF        (-/+ tot)   \n")
        dump.write(" --------------------------------------------------------------------------------------------------------------------------- \n")
        data, fref, fratio = effs[0], TGraphByX(effs[1]), TGraphByX(ratio.syst)
        for i in xrange(data.GetN()):
            x = data.GetX()[i]
            xl = x-data.GetErrorXlow(i)
            xh = x+data.GetErrorXhigh(i)
            y = data.GetY()[i], data.GetErrorYlow(i), data.GetErrorYhigh(i)
            iref = fref[x]; iratio = fratio[x]
            if iref != None:
                       y0 = effs[1].GetY()[iref], effs[1].GetErrorYlow(iref), effs[1].GetErrorYhigh(iref)
            else:      y0 = 0, 0, 0
            if iratio != None:
                       r0 = ratio.GetY()[iratio], ratio.GetErrorYlow(iratio), ratio.GetErrorYhigh(iratio) # stat only
                       r1 = ratio.syst.GetY()[iratio], ratio.syst.GetErrorYlow(iratio), ratio.syst.GetErrorYhigh(iratio) # total ?
                       r2 = ratio.systOnly.GetY()[iratio], ratio.systOnly.GetErrorYlow(iratio), ratio.systOnly.GetErrorYhigh(iratio) # syst only ?
		       print "ratio.GetY()[iratio]:  ", ratio.GetY()[iratio]
		       print "r2: ", r2
		       print "r1: ", r1
            else:      r0 = 1, 1, 1; r1 = 1, 1, 1; r2 = 1, 1, 1
            def peff(e,em,ep): return "%5.1f -%3.1f +%3.1f" % (e*100., max(em,0)*100., max(ep,0)*100.)
            #def psf1(r,rm,rp): return "%5.3f -%5.3f +%5.3f" % (r, max(rm,0), max(rp,0))
            def psf1(r,rm,rp): return "%5.5f -%5.5f +%5.5f" % (r, max(rm,0), max(rp,0))
            #def psf2(rstat,rsyst): return "%5.3f -%5.3f +%5.3f -%5.3f +%5.3f" % (rstat[0], max(rstat[1],0), max(rstat[2],0), max(rsyst[1],0), max(rsyst[2],0))
            def psf2(rstat,rsyst): return "%5.5f -%5.5f +%5.5f -%5.5f +%5.5f" % (rstat[0], max(rstat[1],0), max(rstat[2],0), max(rsyst[1],0), max(rsyst[2],0))
            dump.write("% 5.1f  % 5.1f    %s  %s     %s    %s\n" % (xl,xh, peff(*y), peff(*y0), psf2(r0,r2), psf1(*r1)))
#                                                                          y->MC, y0-> data, psf2-> SF(stat,syst), psf1(tot)				
        dump.close()
def loadFile(name,options):
    tfile = ROOT.TFile.Open(options.inDir+"/"+name+".root")
    if not tfile: print "Can't find file "+name
    data = tfile.Get(name)
    ref  = tfile.Get(name+"_ref")
    truth  = tfile.Get(name+"_ref_truth")
    ret = { 'tfile':tfile, 'data':data, 'ref':ref, 'truth':truth }
    #print "pre test for ret:", ret
    makeRatios(ret)  # adds the ratio of efficiencies TGraph for data and MC efficiencies, and associated unc. in quadrature
#    print "test for ret:", ret
    return ret

class FetchByX: # here here
    def __init__(self,data,withErrors=False):
        self._data = data[:]
        #self._data.sort(key  = lambda (k,v):k)
        self._withErrors = withErrors
    def __getitem__(self,x):
        for (dx,dy) in self._data:
            if abs(x-dx) < 1e-4: return dy # 
        return None
class FetchByX_rms: # here here
    def __init__(self,data,withErrors=False):
        self._data = data[:]
        print "self._data     FetchByX_rms: ", self._data
        #self._data.sort(key  = lambda (k,v):k)
        self._withErrors = withErrors
    def __getitem__(self,x):
        for (dx,dy) in self._data:
        #for dy in self._data:
            #print "dy in FetchByX_rms:  ", dy
            if abs(x-dx) < 1e-4: return dy # 
        return None


class TGraphByX:
    def __init__(self,graph):
        self._graph = graph
        self._x = None
        self._i = None
    def __getitem__(self,x):
        if self._x == None or abs(x-self._x) > 1e-4: 
            self._fetch(x)
        return self._i
    def _fetch(self,x):
        xd = self._graph.GetX()
        for i2 in xrange(self._graph.GetN()):
            if abs(x-xd[i2]) < 1e-4: 
                self._i = i2
                self._x = x
                return i2
        print "could not find ",x," in ",[xd[i] for i in xrange(self._graph.GetN())]
        return None
        
#def diffBbB(numeff,deneff,relative=False):
def diffBbB(numeff,deneff,relative=False, rms=False):
    xn = numeff.GetX()
    yn = numeff.GetY()
    xd = deneff.GetX()
    yd = deneff.GetY()
    ret = {}  # dict
    for i in xrange(numeff.GetN()):
        found = False
        for i2 in xrange(deneff.GetN()):
            if abs(xn[i]-xd[i2]) < 1e-4: 
                found = True; break # for same bin id
        if found:  # relevant
            diff = yn[i]-yd[i2]
            if relative: diff /= yd[i2]
            ret[xn[i]] = diff
        else:
            print "Warning, point at x ",xn[i]," missing in ",deneff.GetName()
            ret[xn[i]] = 0.
    return FetchByX(ret.items()) # ret.items() is the pairs of the bin center and +/- error pairs 

def diffBbB_rms(data,numeff,deneff, deneffs,key,altNames,relative=False): # deneff  -> deneffs (tgraphs of all alts)

    print "diffBbB_rms key:", key
    xn = numeff.GetX()
    #print "xn:", xn
    yn = numeff.GetY() # nominal SF Tgraph
    xd = deneff.GetX() 
    yd = deneff.GetY() # an alternative SF Tgraph
    ret = {}  # dict
    bins = []
    mean_bins = []
    nominal_bins = []
 
    for i in xrange(numeff.GetN()):
        found = False
    	sf_sum = 0
    	if (key=='ratioErr'): print "for bin:   ",i
    	if (key=='ratioErr'): print "nominal SF is :   ",yn[i]
    	nominal_bins.append(yn[i])
    	bins.append(xn[i]) 
    	for i2 in xrange(deneff.GetN()):
            if abs(xn[i]-xd[i2]) < 1e-4: 
                found = True; break # for same bin id
        if found:  # relevant
            sf_sum += yn[i]; # initially nominal
            for alter in deneffs:
    	        sf_sum += alter[key].GetY()[i2] 
    	    sf_mean = sf_sum/(len(deneffs)+1) # div by no. of nominal + alts
    	    mean_bins.append(sf_mean)
            diff = sf_mean - yd[i2]
            if relative: diff /= yd[i2]
            ret[xn[i]] = diff
            numeff.SetPoint(i , xn[i ], sf_mean)
            data[key] = numeff 
        else:
                print "Warning, point at x ",xn[i]," missing in ",deneff.GetName()
                ret[xn[i]] = 0.
    return FetchByX(ret.items()) # ret.items() is the pairs: (bin center, syst. error i.e. diff)
    #return FetchByX(ret.items()), dif2 # ret.items() is the pairs: (bin center, syst. error i.e. diff)

def applyDiff1DAsUncertainty(graph,diff,relative=False,oneSided=False):
    x = graph.GetX()
    for i in xrange(graph.GetN()):
        d = diff[x[i]]
	#print "diff:  ", diff
	print "bin:  ", i
	print "Closure:  d:", abs(d)
        if d is None: continue
        if relative: d *= graph.GetY()[i]
        if oneSided:
            if d > 0: graph.SetPointEYhigh(i, hypot(graph.GetErrorYhigh(i),d))
            else:     graph.SetPointEYlow(i, hypot(graph.GetErrorYlow(i),-d))
        else:
            graph.SetPointEYhigh(i, hypot(graph.GetErrorYhigh(i),abs(d)))
            graph.SetPointEYlow(i, hypot(graph.GetErrorYlow(i),abs(d)))
    return graph

def applyDiff2DAsUncertainty(graph,diff,relative=False):
    x = graph.GetX()
    for i in xrange(graph.GetN()):
        d = diff[x[i]]
	#print "len(diff)", len(diff[[x]])
	print "d is :  ", d
	print "hello diff:    ", diff
        if d is None: continue
        dl,dh = d
	print "dl:   ", dl
	print "dh:   ", dh
        if relative: 
            dh *= graph.GetY()[i]; dl *= graph.GetY()[i]
        graph.SetPointEYhigh(i, hypot(graph.GetErrorYhigh(i),abs(dh)))
        graph.SetPointEYlow(i, hypot(graph.GetErrorYlow(i),abs(dl)))
    return graph

def applyDiff2DAsUncertainty_rms(graph,diff,nalts,relative=False): # # diff is fitShape[ratio]
    x = graph.GetX()
    for i in xrange(graph.GetN()):
        d = diff[x[i]] # pair of systs.
#        print "applyDiff2DAsUncertainty_rms   d is :  ", d
	#print "len(diff)", len(diff[[x]])
#        print "hello diff:    ", diff
#        print "hello nalts:    ", nalts
        if d is None: continue
        dl,dh = d 
	print "bin:   ", i
        print "dl:   ", dl
        print "dh:   ", dh
	print "nominal stat. graph.GetErrorYhigh(",i,")", graph.GetErrorYhigh(i)
	print "nominal stat. graph.GetErrorYlow(",i,")", graph.GetErrorYlow(i)
        if relative: 
            dh *= graph.GetY()[i]; dl *= graph.GetY()[i]
        #graph.SetPointEYhigh(i, hypot(graph.GetErrorYhigh(i),abs(dh)/sqrt(nalts))) # data stat + systs. rms
        #graph.SetPointEYlow(i, hypot(graph.GetErrorYlow(i),abs(dl)/sqrt(nalts)))
        graph.SetPointEYhigh(i, hypot(graph.GetErrorYhigh(i),abs(dh))) # data,MC stat + systs. rms
        graph.SetPointEYlow(i, hypot(graph.GetErrorYlow(i),abs(dl)))
    return graph


def capErrors(graph):
    for i in xrange(graph.GetN()):
        y = graph.GetY()[i]
        yhi = graph.GetErrorYhigh(i)
        ylo = graph.GetErrorYlow(i)
        if y+yhi > 1.0: graph.SetPointEYhigh(i, max(1.0-y,0))
        if y-ylo < 0.0: graph.SetPointEYlo(i, max(y,0))

def diffAsGraphBand(graph,diff,relative=False):
    x = graph.GetX()
    y = graph.GetY()
    ret = ROOT.TGraphAsymmErrors(graph.GetN())
    for i in xrange(graph.GetN()):
        d = diff[x[i]]
        if d is None: dl,dh = 0.,0.
        elif type(d) == float:  dl,dh = -abs(d),abs(d)
        else: dl,dh = d
        if relative: 
            dh *= graph.GetY()[i]; dl *= graph.GetY()[i]
        graph.SetPoint(i, x[i], y[i])
        graph.SetPointError(i, graph.GetErrorXlow(i), graph.GetErrorXhigh(i), -dl, dh)
    return graph


#def envelopeOfDiffs_rms(graph,diffs): # returns list with pair of bin and rms systs values in sub-pair
def envelopeOfDiffs_rms(graph,diffs,altNames): # returns list with pair of bin and rms systs values in sub-pair
    x = graph.GetX()
    ret = []
    for i in xrange(graph.GetN()):
        dvals = [d[x[i]] for d in diffs]
	print "bin no. i:      ", i
	print "altNames:    ", altNames
	print "dvals:  ", dvals
        #ret.append((x[i], (min(dvals),max(dvals))))
	sqr_sum = 0
        for j in range(len(dvals)): 
	    print "j: ", j, "dvals[j]:  ", dvals[j]
	    sqr_sum+= dvals[j]*dvals[j]
	print "sqr_sum: ", sqr_sum
        #ret.append((x[i], (min(dvals),max(dvals)))) # existing envelope approach

#        ret.append((x[i], (sqrt(sqr_sum/(len(dvals)-1)),sqrt(sqr_sum/(len(dvals)-1)))))  # RMS as given on https://indico.cern.ch/event/1233959/contributions/5310383/attachments/2661218/4610258/07062023_HZZworkshop_lowptstudies_AnaSculac.pdf
        #ret.append((x[i], (sqrt(sqr_sum/(len(dvals)-1))/sqrt(len(dvals)),sqrt(sqr_sum/(len(dvals)-1))/sqrt(len(dvals)))))  # RMS as given on https://indico.cern.ch/event/1233959/contributions/5310383/attachments/2661218/4610258/07062023_HZZworkshop_lowptstudies_AnaSculac.pdf
        ret.append((x[i], (sqrt(sqr_sum/(len(dvals)))/sqrt(len(dvals)+1),sqrt(sqr_sum/(len(dvals)))/sqrt(len(dvals)+1))))  # RMS as given on https://indico.cern.ch/event/1233959/contributions/5310383/attachments/2661218/4610258/07062023_HZZworkshop_lowptstudies_AnaSculac.pdf
        #print "ret:   ", ret
    #print "FetchByX(ret):  ", FetchByX(ret)
    #print "ret: input to the FetchByX_rms in envelopeOfDiffs_rms  ", ret # has (bin,(min of the systs, max of the systs)) 
    #print "FetchByX(ret):   ",FetchByX(ret)
    #return FetchByX(ret)
    return FetchByX_rms(ret)

def envelopeOfDiffs(graph,diffs):
    x = graph.GetX()
    ret = []
    for i in xrange(graph.GetN()):
        dvals = [d[x[i]] for d in diffs]
        ret.append((x[i], (min(dvals),max(dvals))))
    #print "ret: input to the FetchByX in envelopeOfDiffs  ", ret
    return FetchByX(ret)



def closureSystematic(data):
    return diffBbB(data['ref'],data['truth'],relative=True)    

#def fitShapeSystematic(data,alts,key): # data and alts are TGraphs of nominal and alt. SF resp
def fitShapeSystematic(data,alts,key,altNames): # data(main) and alts are TGraphs of nominal and alt. SF resp
# key is data, ref and ratio
    if (key.startswith("ratio")): 
	    print "key (ratio) is:   ", key, "    SF update check for bin0 before: ",data[key].GetY()[0] 
	    diffs =  [diffBbB_rms(data,data[key],alt[key],alts,key,altNames) for alt in alts ] # assigns nominal the mean SF, and add difference w.r.t mean SF
	    print "SF update check for bin0 after: ",data[key].GetY()[0];# return envelopeOfDiffs_rms(data[key],diffs,altNames) 
	    return envelopeOfDiffs_rms(data[key],diffs,altNames) 
#        return envelopeOfDiffs_rms(data[key],diffs,altNames) # gets the (bin,syst. rms, syst. rms) .
    else: 
        print "key (non-ratio) is:      ", key; #diffs = [ diffBbB(data[key],alt[key]) for alt in alts ]
        diffs = [ diffBbB(data[key],alt[key]) for alt in alts ]
#	    diffs = [ diffBbB(data[key],alt[key]) for alt in alts ]
        return envelopeOfDiffs(data[key],diffs)

def graphQSub(gsyst,gstat):
    gonly = gsyst.Clone()
    for i in xrange(gonly.GetN()):
	if i == 0: print "For bin0, syst up is:    ", hypsub(gsyst.GetErrorYhigh(i),gstat.GetErrorYhigh(i))
        gonly.SetPointEYhigh(i, hypsub(gsyst.GetErrorYhigh(i),gstat.GetErrorYhigh(i)))
        gonly.SetPointEYlow(i, hypsub(gsyst.GetErrorYlow(i),gstat.GetErrorYlow(i)))
    return gonly 

def addTnPHarvestOptions(parser):
    parser.add_option("-t", "--tree",    dest="tree", default='tree', help="Pattern for tree name");
    parser.add_option("-s", "--signalModel",   dest="sigModel", default='voigt', help="Signal model");
    parser.add_option("-b", "--backgroundModel",   dest="bkgModel", default='expo', help="Background model");
    parser.add_option("--salt", "--altSignalModel",   dest="altSigModel", default=[], action="append", help="Signal model");
    parser.add_option("--balt", "--altBackgroundModel",   dest="altBkgModel", default=[], action="append", help="Background model");
    parser.add_option("--alt", "--altSetup",   dest="altSetups", default=[], action="append", help="Alternate setups (to be used with the nominal S & B model)");
    parser.add_option("--exclude", "--exclude", dest="exclude", type="string", default=[], action="append", nargs=2, help="make a single fit");
    parser.add_option("-N", "--name",    dest="name", type="string", help="name", default="eff")
    parser.add_option("--xtitle",   dest="xtitle", type="string", default=None, help="X title")
    parser.add_option("--ytitle",   dest="ytitle", type="string", default="Efficiency", help="Y title")
    parser.add_option("--mtitle",   dest="mtitle", type="string", default="Mass (GeV)", help="M title")
    parser.add_option("--pdir", "--print-dir", dest="printDir", type="string", default="plots", help="print out plots in this directory");
    parser.add_option("--idir", "--in-dir", dest="inDir", type="string", default="plots", help="print out plots in this directory");
    parser.add_option("--yrange", dest="yrange", type="float", nargs=2, default=(0,1.025));
    parser.add_option("--rrange", dest="rrange", type="float", nargs=2, default=None);
    parser.add_option("--doRatio", dest="doRatio", action="store_true", default=False, help="Add a ratio plot at the bottom")


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] tree reftree")
    addTnPHarvestOptions(parser)
    (options, args) = parser.parse_args()
    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine(".x ~/cpp/tdrstyle.cc")
    ROOT.gStyle.SetOptStat(0)
    if not os.path.exists(options.printDir):
        os.system("mkdir -p %s" % options.printDir)
        os.system("cp /afs/cern.ch/user/g/gpetrucc/php/index.php  %s/" % options.printDir)
    if not os.path.exists(options.inDir):
        raise RuntimeError, "Input directory missin"
    print "options.name:  ", options.name
    pieces = options.name.split("_",1)
    pattern = "%s_%%s_%%s_%s" % (pieces[0], pieces[1])
    nominal = pattern % (options.sigModel, options.bkgModel)
    allsigs = [ options.sigModel ] + options.altSigModel
    allbkgs = [ options.bkgModel ] + options.altBkgModel
    altmods = [ (s,b) for s in allsigs for b in allbkgs if (s,b) != (options.sigModel, options.bkgModel) and (s,b) not in options.exclude ]
    altNames = [ pattern % (s,b) for (s,b) in altmods ]
    altNames += [ pattern % (options.sigModel, options.bkgModel+"_"+altSetup) for altSetup in options.altSetups ]
    
    main = loadFile(nominal, options)  # has SF information for nominal, TGraphAsy
    print "done for nominal  "
    alts = [ loadFile(alt, options) for alt in altNames ] # has SF information for all alternatives, TGraphAsy
    print "nominal:   ", nominal
    print "altNames:   ", altNames
#    print "main:", main #, "alts: ", alts
#    print "alts: ", alts
    closure = closureSystematic(main) # takes difference of MC and truth efficiencies
    nalts= len(alts)
    print "nalts:   ", nalts
    #fitShape = dict([ (x,fitShapeSystematic(main, alts, x)) for x in ("data","ref","ratio") ]) # has bin informa with the systematics min and max from the systs in rms (bin, rms, rms)
    #fitShape = dict([ (x,fitShapeSystematic(main, alts, x)) for x in ("data","ref","ratio", "ratioErr") ]) # has bin informa with the systematics min and max from the systs in rms (bin, rms, rms)
    fitShape = dict([ (x,fitShapeSystematic(main, alts, x, altNames)) for x in ("data","ref","ratio", "ratioErr") ]) # has bin informa with the systematics min and max from the systs in rms (bin, rms, rms)
    print "fitShape: ", fitShape
#    print "main[ratio].GetY()[0]", main["ratio"].GetY()[0]
#    print "main[ratio].GetY()[1]", main["ratio"].GetY()[1]
    for k in "data","ref","ratio","ratioErr":
        syst = main[k].Clone() # has information of nominal case each case of "k", meant to be statOnly
	if k=="ratioErr": print "testing statOnly::   syst.GetErrorYlow(1):  ", syst.GetErrorYlow(1)
	if k=="ratioErr": print "testing statOnly::   syst.GetErrorYhigh(1):  ", syst.GetErrorYhigh(1)
	#print "syst: ", syst

        applyDiff1DAsUncertainty(syst,closure,relative=True,oneSided=False) # closure has MC and truth efficiencies diffs. function adds in quadrature the closure output into the syst. ("data","ref","ratio","ratioErr")
	if k=="ratioErr": print "testing statOnly + MC closure ??  ::   syst.GetErrorYlow(1):  ", syst.GetErrorYlow(1)
	if k=="ratioErr": print "testing statOnly + MC closure ??  ::   syst.GetErrorYhigh(1):  ", syst.GetErrorYhigh(1)
        #if k == "ratio": # x is always ratio in the loop
        if (k.startswith("ratio")): # x is always ratio in the loop
	    print "x is :        ", x
	    #applyDiff2DAsUncertainty_rms(syst,fitShape[x]) # syst is nominal, w.r.t which difference is to be taken
	    applyDiff2DAsUncertainty_rms(syst,fitShape[x], nalts) # syst is nominal, w.r.t which difference is to be taken. this inherits nominal (mean of alts..) with stat(data,MC) added. And fitShape has list of systs(rms) 
	else:
	    print "x is 2    :        ", x
            applyDiff2DAsUncertainty(syst,fitShape[x]) # syst is nominal, w.r.t which difference is to be taken
        main[k].syst = syst # syst is now with total unc. (MC closure syst + RMS syst + stat (data+MC))
	#if k=="ratio": 
	if k=="ratioErr": 
		print "testing statOnly::   main[k].GetErrorYlow(1):  ", main[k].GetErrorYlow(1)
		print "testing statOnly + syst. (RMS)::   main[k].syst.GetErrorYlow(1):  ", main[k].syst.GetErrorYlow(1)
        
        main[k].systOnly = graphQSub(syst, main[k]) # quadarature diff(total, statOnly), main[k] is meant to be statOnly
	if k=="ratioErr":
	    print "testing systOnly::   main[k].systOnly.GetErrorYlow(1):  ", main[k].systOnly.GetErrorYlow(1)
        if k in ("data","ref"): 
            capErrors(main[k])
#	    print "k: ", k, "              capErrors: ", capErrors(main[k])
            capErrors(main[k].syst)
            capErrors(main[k].systOnly)
    plotEffs(options.name, [ main['data'], main['ref'] ], main['ratioErr'], options) # orig
    #plotEffs(options.name, [ main['data'], main['ref'] ], main['ratio'], options) # TJ
    fout = ROOT.TFile.Open(options.printDir+"/"+options.name+".root", "RECREATE")
    for k in "data","ref","ratio","ratioErr":
	print "k:  ", k
	if (k.startswith("ratio")): print "testing3::   main[k].syst.GetErrorYlow(0):  ", main[k].syst.GetErrorYlow(0)
	if (k.startswith("ratio")): print "testing4::   main[k].GetErrorYlow(0):  ", main[k].GetErrorYlow(0)
        print "testing5::   main[ratioErr].GetErrorYlow(0):  ", main["ratioErr"].GetErrorYlow(0)
        fout.WriteTObject(main[k], k) # syst only
        fout.WriteTObject(main[k].syst, k+"_syst") # total
	print "k:", k
	print "main[k].syst: ", main[k].syst 
    fout.Close()
    

