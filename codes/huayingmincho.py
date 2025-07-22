import os, sys, json
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables

pydir = os.path.abspath(os.path.dirname(__file__))

fontver='1.016'
fontname='HuayingMincho'
tcname='華英明朝'
scname='华英明朝'
janame='華英明朝'
vendorURL='https://github.com/GuiWonder/HuayingMincho'
VendID='GUIF'
Copyright='Copyright(c) '+fontname+', 2022-2025. You must accept "https://opensource.org/licenses/IPA/" to use this product.'

def getstdic():
	newdic=dict()
	with open(os.path.join(pydir, 'datas/stoneo.dt'),'r',encoding='utf-8') as f:
		for line in f.readlines():
			litm=line.split('#')[0].strip()
			if '-' not in litm: continue
			s, t=litm.split(' ')[0].split('-')
			s, t=s.strip(), t.strip()
			if s and t and s!=t:
				newdic[s]=t
	for s, t in list(newdic.items()):
		if t in newdic: newdic[s]=newdic[t]
	newlst=list()
	with open(os.path.join(pydir, 'datas/stonem.dt'),'r',encoding='utf-8') as f:
		for line in f.readlines():
			litm=line.split('#')[0].strip()
			if '-' not in litm: continue
			dic1=dict()
			ls=litm.strip().split(' ')
			s, t=ls[0].split('-')
			dic1['s'], dic1['t']=s, t
			dic1['p']=ls[1:]
			newlst.append(dic1)
	return newdic, newlst

def stlookups(font):
	cmap=font.getBestCmap()
	chrdic, phrdic=getstdic()
	for s, t in list(chrdic.items()):
		if ord(s) not in cmap and ord(t) in cmap:
			setcg(font['cmap'], ord(s), cmap[ord(t)])

	cmap=font.getBestCmap()
	glod=font.getGlyphOrder()
	stmul=otTables.Lookup()
	stsig=otTables.Lookup()
	stsig1=otTables.Lookup()
	stsig2=otTables.Lookup()
	stsig3=otTables.Lookup()
	stlkups=[stmul, stsig, stsig1, stsig2, stsig3]
	sgtb, sgtb1, sgtb2, sgtb3=dict(), dict(), dict(), dict()
	for lk in stlkups[1:]:
		lk.LookupType=1
		lk.LookupFlag=0
	sgsb=otTables.SingleSubst()
	sgsb1=otTables.SingleSubst()
	sgsb2=otTables.SingleSubst()
	sgsb3=otTables.SingleSubst()
	stsig.SubTable=[sgsb]
	stsig1.SubTable=[sgsb1]
	stsig2.SubTable=[sgsb2]
	stsig3.SubTable=[sgsb3]
	stmul.SubTable=list()
	stmul.LookupType=6
	stmul.LookupFlag=0
	ltc=dict()
	for phdc in phrdic:
		s, t=phdc['s'], phdc['t']
		dics=phdc['p']
		sg=cmap[ord(s)]
		tg=cmap[ord(t)]
		i=dics.index(s)
		assert i>-1
		bkcov=dics[0:i]
		bkcov.reverse()
		lahcov=dics[i+1:]
		if sg!=tg and tg not in ltc:
			if sg not in sgtb1:
				sgtb1[sg]=tg
				ltc[tg]=2
			elif sg not in sgtb2:
				sgtb2[sg]=tg
				ltc[tg]=3
			elif sg not in sgtb3:
				sgtb3[sg]=tg
				ltc[tg]=4
			else:
				raise
		bklst=list()
		for strs in bkcov:
			cvobjbk=otTables.Coverage()
			cvobjbk.glyphs=list(set([cmap[ord(ch)] for ch in strs]))
			assert len(cvobjbk.glyphs)>0, strs
			cvobjbk.glyphs=list(sorted([g for g in cvobjbk.glyphs], key=lambda g:glod.index(g)))
			bklst.append(cvobjbk)
		ahlst=list()
		for strs in lahcov:
			cvobjah=otTables.Coverage()
			cvobjah.glyphs=list(set([cmap[ord(ch)] for ch in strs]))
			assert len(cvobjah.glyphs)>0, strs
			cvobjah.glyphs=list(sorted([g for g in cvobjah.glyphs], key=lambda g:glod.index(g)))
			ahlst.append(cvobjah)
		cvobjip=otTables.Coverage()
		cvobjip.glyphs=[cmap[ord(s)]]
		mulsb=otTables.ChainContextSubst()
		mulsb.Format=3
		mulsb.BacktrackCoverage=bklst
		mulsb.InputCoverage=[cvobjip]
		mulsb.LookAheadCoverage=ahlst
		if sg!=tg:
			sblrd=otTables.SubstLookupRecord()
			sblrd.SequenceIndex=0
			sblrd.LookupListIndex=ltc[tg]
			mulsb.SubstLookupRecord=[sblrd]
		stmul.SubTable.append(mulsb)
	sgsb1.mapping=sgtb1
	sgsb2.mapping=sgtb2
	sgsb3.mapping=sgtb3
	for s, t in list(chrdic.items()):
		if ord(s) in cmap and ord(t) in cmap and cmap[ord(s)]!=cmap[ord(t)]:
			sgtb[cmap[ord(s)]]=cmap[ord(t)]
	sgsb.mapping=sgtb
	for lkp in font["GSUB"].table.LookupList.Lookup:
		for st in lkp.SubTable:
			if st.LookupType in (5, 6) and hasattr(st, 'SubstLookupRecord'):
				for sbrcd in st.SubstLookupRecord:
					sbrcd.LookupListIndex+=len(stlkups)
	for ft in font["GSUB"].table.FeatureList.FeatureRecord:
		ft.Feature.LookupListIndex=[i+len(stlkups) for i in ft.Feature.LookupListIndex]
	font["GSUB"].table.LookupList.Lookup=stlkups+font["GSUB"].table.LookupList.Lookup
	stft=otTables.FeatureRecord()
	stft.Feature=otTables.Feature()
	stft.FeatureTag='ccmp'
	stft.Feature.LookupListIndex=[0, 1]
	font["GSUB"].table.FeatureList.FeatureRecord.insert(0, stft)
	for sr in font["GSUB"].table.ScriptList.ScriptRecord:
		sr.Script.DefaultLangSys.FeatureIndex=[i+1 for i in sr.Script.DefaultLangSys.FeatureIndex]
		sr.Script.DefaultLangSys.FeatureIndex.insert(0, 0)
		for lsr in sr.Script.LangSysRecord:
			lsr.LangSys.FeatureIndex=[i+1 for i in lsr.LangSys.FeatureIndex]
			lsr.LangSys.FeatureIndex.insert(0, 0)


def fontinf(font, style):
	nameen, nametc, namesc, nameja=str(), str(), str(), str()
	if style=='1':
		nameen=fontname+' Old'
		nametc=tcname+' 舊印體'
		namesc=scname+' 旧印体'
		nameja=janame+' Old'
	elif style=='2':
		nameen=fontname+' Classic'
		nametc=tcname+' 傳承體'
		namesc=scname+' 传承体'
		nameja=janame+' Classic'
	elif style=='3':
		nameen=fontname+' ODict'
		nametc=tcname+' 舊典體'
		namesc=scname+' 旧典体'
		nameja=janame+' ODict'
	elif style=='4':
		nameen=fontname+' T'
		nametc=tcname+' 繁體'
		namesc=scname+' 繁体'
		nameja=janame+' T'

	subfamily='Regular'
	psName=nameen.replace(' ', '')
	uniqID=nameen+' Version '+fontver
	License=LicenseUrl='https://opensource.org/licenses/IPA/'
	
	newnane=newTable('name')
	
	for pe, li in ((0, 0), (1, 11), (2, 19), (25, 33)):
		newnane.setName(Copyright, 0, 1, pe, li)
		newnane.setName(subfamily, 2, 1, pe, li)
		newnane.setName(uniqID, 3, 1, pe, li)
		newnane.setName('Version '+fontver, 5, 1, pe, li)
		newnane.setName(psName, 6, 1, pe, li)
		newnane.setName(vendorURL, 11, 1, pe, li)
		newnane.setName(License, 13, 1, pe, li)
		newnane.setName(LicenseUrl, 14, 1, pe, li)
		
	newnane.setName(nameen, 1, 1, 0, 0)
	newnane.setName(nameen, 4, 1, 0, 0)
	newnane.setName(nameja, 1, 1, 1, 11)
	newnane.setName(nameja, 4, 1, 1, 11)
	newnane.setName(nametc, 1, 1, 2, 19)
	newnane.setName(nametc, 4, 1, 2, 19)
	newnane.setName(namesc, 1, 1, 25, 33)
	newnane.setName(namesc, 4, 1, 25, 33)
	
	for lanid in (1033, 1028, 3076, 5124, 2052, 4100, 1041):
		newnane.setName(Copyright, 0, 3, 1, lanid)
		newnane.setName(subfamily, 2, 3, 1, lanid)
		newnane.setName(uniqID, 3, 3, 1, lanid)
		newnane.setName('Version '+fontver, 5, 3, 1, lanid)
		newnane.setName(psName, 6, 3, 1, lanid)
		newnane.setName(vendorURL, 11, 3, 1, lanid)
		newnane.setName(License, 13, 3, 1, lanid)
		newnane.setName(LicenseUrl, 14, 3, 1, lanid)

	newnane.setName(nameen, 1, 3, 1, 1033)
	newnane.setName(nameen, 4, 3, 1, 1033)
	newnane.setName(nameja, 1, 3, 1, 1041)
	newnane.setName(nameja, 4, 3, 1, 1041)
	for lanid in (1028, 3076, 5124):
		newnane.setName(nametc, 1, 3, 1, lanid)
		newnane.setName(nametc, 4, 3, 1, lanid)
	for lanid in (2052, 4100):
		newnane.setName(namesc, 1, 3, 1, lanid)
		newnane.setName(namesc, 4, 3, 1, lanid)
	return newnane

def prouv(font, ispr):
	cmap=font.getBestCmap()
	for table in font["cmap"].tables:
		if table.format==14:
			for vsl in table.uvsDict.keys():
				newl=list()
				for cg in table.uvsDict[vsl]:
					if cg[1]==None and ispr:
						newl.append((cg[0], cmap[cg[0]]))
					elif cg[0] in cmap and cg[1]==cmap[cg[0]] and not ispr:
						newl.append((cg[0], None))
					else:
						newl.append((cg[0], cg[1]))
				table.uvsDict[vsl]=newl
def getuvs(fonto):
	nuv=dict()
	for table in fonto['cmap'].tables:
		if table.format==14:
			for vsl in table.uvsDict.keys():
				for cg in table.uvsDict[vsl]:
					if cg[0] not in nuv:
						nuv[cg[0]]=dict()
					if cg[1]==None:
						raise
					else:
						nuv[cg[0]][vsl]=cg[1]
	return nuv

def setcg(cmap, code, glyf):
	for table in cmap.tables:
		if (table.format==4 and code<=0xFFFF) or table.format==12 or code in table.cmap:
			table.cmap[code]=glyf

def addvariants(font):
	print('Processing font variants...')
	with open(os.path.join(pydir, 'datas/Variants.txt'),'r',encoding = 'utf-8') as f:
		cmap=font.getBestCmap()
		for line in f.readlines():
			litm=line.split('#')[0].strip()
			if '\t' not in litm: continue
			vari=litm.strip().split('\t')
			gtgly=str()
			for ch1 in vari:
				if ord(ch1) in cmap:
					gtgly=cmap[ord(ch1)]
					break
			if gtgly:
				for ch1 in vari:
					if ord(ch1) not in cmap:
						# print(ch1)
						setcg(font['cmap'], ord(ch1), gtgly)

def savefont(outfile, font, IsT=False):
	outfont=TTFont(inf)
	outfont['OS/2'].achVendID=VendID
	outfont['head'].fontRevision=float(fontver)

	outfont['name']=font['name']
	outfont['cmap']=font['cmap']
	if IsT:
		outfont['GSUB']=font['GSUB']
	outfont.save(outfile)

print('====Start Build HuayingMincho Fonts====\n')
inf, outf, style=str(), str(), str()
if len(sys.argv)>3 and sys.argv[3] in ('1', '2', '3'):
	inf=sys.argv[1]
	outf=sys.argv[2]
	style=sys.argv[3]
else:
	sys.exit()

print('Loading font...')
font = TTFont(inf)
prouv(font, True)

exch=set()
uvss=getuvs(font)

cmap=font.getBestCmap()
newmap=dict()

if style=='2':
	with open(os.path.join(pydir, 'datas/mulcodechar.txt'), 'r', encoding='utf-8') as f:
		for line in f.readlines():
			litm=line.split('#')[0].strip()
			if '-' not in litm: continue
			a=litm.split(' ')[0].split('-')
			exch.add(a[0])
			if ord(a[1]) in cmap:
				newmap[ord(a[0])]=cmap[ord(a[1])]
with open(os.path.join(pydir, 'datas/mulcodevar.txt'), 'r', encoding='utf-8') as f:
	for line in f.readlines():
		litm=line.split('#')[0].strip()
		if '\t' not in litm: continue
		a=litm.split('\t')
		if style=='3' and a[0]=='即': continue
		
		newmap[ord(a[0])]=uvss[ord(a[1])][int(a[2].split(' ')[1].strip(), 16)]
		newmap[ord(a[1])]=uvss[ord(a[1])][int(a[3].split(' ')[1].strip(), 16)]
		exch.add(a[0])

with open(os.path.join(pydir, 'datas/uvs-get-MARK-0'+style+'.txt'), 'r', encoding='utf-8') as f:
	for line in f.readlines():
		litm=line.split('#')[0].strip()
		if litm.endswith('X'):
			a=litm.split(' ')
			if a[0] not in exch:
				newmap[ord(a[0])]=uvss[ord(a[0])][int(a[3].strip('X').strip(), 16)]

print('Moving codes...')

for c in newmap.keys():
	setcg(font['cmap'], c, newmap[c])

print('Checking variants...')
addvariants(font)

prouv(font, False)
print('Setting font info...')
font['name']=fontinf(font, style)
print('Generating font(s)...')

if len(sys.argv)>4 and sys.argv[4].lower()=='t' and os.path.isdir(outf):
	outname=os.path.join(outf, font["name"].getDebugName(6)+'.ttf')
	savefont(outname, font)

	font['name']=fontinf(font, '4')
	print('Convert to TC...')
	stlookups(font)
	outname=os.path.join(outf, font["name"].getDebugName(6)+'.ttf')
	savefont(outname, font, True)

else:
	savefont(outf, font)

print('Finished!')
