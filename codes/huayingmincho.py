import os, sys, json
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables
from datetime import datetime

pydir = os.path.abspath(os.path.dirname(__file__))
cfg=json.load(open(os.path.join(pydir, 'config.json'), 'r', encoding='utf-8'))
varbl={'1':'Old', '2':'Classic', '3':'ODict'}

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
	for s in list(newdic.keys()):
		while newdic[s] in newdic: newdic[s]=newdic[newdic[s]]
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
	def newlk(lktype, flag=0):
		lk=otTables.Lookup()
		lk.LookupType=lktype
		lk.LookupFlag=flag
		lk.SubTable=list()
		return lk
	stmul=newlk(6)
	stsig=newlk(1)
	mylkps=[stmul, stsig]
	exmps=list()
	tglki=dict()
	for phdc in phrdic:
		s, t=phdc['s'], phdc['t']
		sg, tg=cmap[ord(s)], cmap[ord(t)]
		if sg!=tg and tg not in tglki:
			for i, m in enumerate(exmps):
				if sg not in m:
					m[sg]=tg
					tglki[tg]=len(mylkps)+i
					break
			else:
				tglki[tg]=len(mylkps)+len(exmps)
				exmps.append({sg:tg})
		dics=phdc['p']
		i=dics.index(s)
		assert i>-1
		bkcov=dics[0:i]
		bkcov.reverse()
		lahcov=dics[i+1:]
		bklst, ahlst=list(), list()
		for lst, cov in [(bklst, bkcov), (ahlst, lahcov)]:
			for strs in cov:
				glyphs=set([cmap[ord(ch)] for ch in strs])
				assert len(glyphs)>0, strs
				cvobj=otTables.Coverage()
				cvobj.glyphs=sorted(glyphs, key=lambda g:glod.index(g))
				lst.append(cvobj)
		cvobjip=otTables.Coverage()
		cvobjip.glyphs=[sg]
		mulsb=otTables.ChainContextSubst()
		mulsb.Format=3
		mulsb.BacktrackCoverage=bklst
		mulsb.InputCoverage=[cvobjip]
		mulsb.LookAheadCoverage=ahlst
		if sg!=tg:
			sblrd=otTables.SubstLookupRecord()
			sblrd.SequenceIndex=0
			sblrd.LookupListIndex=tglki[tg]
			mulsb.SubstLookupRecord=[sblrd]
		stmul.SubTable.append(mulsb)
	for mp in exmps:
		exsb=otTables.SingleSubst()
		exsb.mapping=mp
		exlk=newlk(1)
		exlk.SubTable=[exsb]
		mylkps.append(exlk)
	sgtb=dict()
	for s, t in list(chrdic.items()):
		if ord(s) in cmap and ord(t) in cmap and cmap[ord(s)]!=cmap[ord(t)]:
			sgtb[cmap[ord(s)]]=cmap[ord(t)]
	sgsb=otTables.SingleSubst()
	sgsb.mapping=sgtb
	stsig.SubTable=[sgsb]
	offset=len(mylkps)
	lklst=font['GSUB'].table.LookupList
	ftlst=font['GSUB'].table.FeatureList
	srlst=font['GSUB'].table.ScriptList
	for lkp in lklst.Lookup:
		for st in lkp.SubTable:
			if st.LookupType in (5, 6):
				if hasattr(st, 'SubstLookupRecord'):
					for sbrcd in st.SubstLookupRecord:
						sbrcd.LookupListIndex+=offset
				if hasattr(st, 'ChainSubClassSet'):
					for rul in st.ChainSubClassSet:
						if hasattr(rul, 'ChainSubClassRule'):
							for subr in rul.ChainSubClassRule:
								for sbrcd in subr.SubstLookupRecord:
									sbrcd.LookupListIndex+=offset
	lklst.Lookup=mylkps+lklst.Lookup
	for ft in ftlst.FeatureRecord:
		ft.Feature.LookupListIndex=[i+offset for i in ft.Feature.LookupListIndex]
	mytg='ccmp'
	tgidxs=[i for i, r in enumerate(ftlst.FeatureRecord) if r.FeatureTag==mytg]
	if tgidxs:
		for idx in tgidxs:
			feat=ftlst.FeatureRecord[idx].Feature
			ftlks={0, 1}
			ftlks.update(feat.LookupListIndex)
			feat.LookupListIndex=sorted(ftlks)
			feat.LookupCount=len(feat.LookupListIndex)
	else: raise

def fontinf(font, style):
	nmdic=dict()
	lans=['EN', 'JA', 'TC', 'SC']
	mac_enc=[(0, 0), (1, 11), (2, 19), (25, 33)]
	win_lan=[[1033, ], [1041, ], [1028, 3076, 5124], [2052, 4100]]
	for l in lans:
		if l in cfg: tfname=cfg[l]['Name']+' '+cfg[l][style]
		else: tfname=cfg['Name']+' '+style
		nmdic[l]={'nm':tfname}
	for i,l in enumerate(lans):
		nmdic[l]['menc']=mac_enc[i]
		nmdic[l]['wlan']=win_lan[i]
	subfamily='Regular'
	ftname=nmdic['EN']['nm']
	psname=ftname.replace(' ', '')
	Version='Version '+cfg['Version']
	uniqID=ftname+' '+Version
	VURL=cfg['VURL']
	License=LicenseUrl=cfg['LicenseUrl']
	Copyright=cfg['Copyright'].format(name=cfg['Name'], year=datetime.now().year)
	newnane=newTable('name')
	for l in lans:
		pe, li=nmdic[l]['menc']
		locname=nmdic[l]['nm']
		idmap={0:Copyright, 1:locname, 2:subfamily, 3:uniqID, 4:locname,
			5:Version, 6:psname, 11:VURL, 13:License, 14:LicenseUrl
			}
		for i, v in idmap.items():
			newnane.setName(v, i, 1, pe, li)
		for lanid in nmdic[l]['wlan']:
			for i, v in idmap.items():
				newnane.setName(v, i, 3, 1, lanid)
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

def main(inf, outf, style, istc):
	print('====Start Build HuayingMincho Fonts====\n')
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
	if istc: stlookups(font)
	prouv(font, False)
	print('Setting font info...')
	vnm='T' if istc else varbl[style]
	font['name']=fontinf(font, vnm)
	print('Generating font(s)...')
	with TTFont(inf, recalcTimestamp=False) as outfont:
		outfont['OS/2'].achVendID=cfg['ID']
		outfont['head'].fontRevision=float(cfg['Version'])
		cptb=['name', 'cmap']
		if istc: cptb.append('GSUB')
		for tb in cptb: outfont[tb]=font[tb]
		outfont.save(outf)

	print('Finished!')

if __name__ == '__main__':
	if len(sys.argv)>3 and sys.argv[3][0] in varbl:
		v=sys.argv[3]
		istc=len(v)>1 and v[1].lower()=='t'
		main(sys.argv[1], sys.argv[2], v[0], istc)
	else:
		sys.exit(1)
