import os, json, fontforge, subprocess, platform, sys

pydir = os.path.abspath(os.path.dirname(__file__))

fontver='1.002'
fontname='HuayingMincho'
tcname='華英明朝'
scname='华英明朝'
vendorURL='https://github.com/GuiWonder/HuayingMincho'

def ckfile(f):
	f=f.strip()
	if not os.path.isfile(f):
		if os.path.isfile(f.strip('"')):
			return f.strip('"')
		elif os.path.isfile(f.strip("'")):
			return f.strip("'")
	return f

def getallcodesname(font, code_glyph, glyph_codes):
	code_glyph.clear()
	glyph_codes.clear()
	for gls in font.glyphs():
		glyph_codes[gls.glyphname]=list()
		if gls.unicode > -1:
			code_glyph[gls.unicode]=gls.glyphname
			glyph_codes[gls.glyphname].append(gls.unicode)
		if gls.altuni != None:
			for uni in gls.altuni:
				if uni[1] <= 0:
					code_glyph[uni[0]] = gls.glyphname
					glyph_codes[gls.glyphname].append(uni[0])

def addvariants():
	with open(os.path.join(pydir, 'datas/Variants.txt'), 'r', encoding = 'utf-8') as f:
		for line in f.readlines():
			line = line.strip()
			if line.startswith('#') or '\t' not in line:
				continue
			vari = line.strip().split('\t')
			codein = 0
			for ch1 in vari:
				chcode = ord(ch1)
				if chcode in code_glyph:
					codein = chcode
					break
			if codein != 0:
				for ch1 in vari:
					chcode = ord(ch1)
					if chcode not in code_glyph:
						mvcodetocode(chcode, codein)

def addglyuni(gly, uni):
	if uni in code_glyph:
		if code_glyph[uni]==gly:
			return
		rmcode(code_glyph[uni], uni)
	adduni(gly, uni)

def unimvtogly(uni, gly):
	if code_glyph[uni]==gly:
		return
	rmcode(code_glyph[uni], uni)
	adduni(gly, uni)

def mvcodetocode(uni, unito):
	if unito not in code_glyph:
		return
	gto=code_glyph[unito]
	if uni in code_glyph:
		gf=code_glyph[uni]
		if gf==gto:
			return
		rmcode(gf, uni)
	adduni(gto, uni)

def rmcode(gly, uni):
	glyph_codes[gly].remove(uni)
	del code_glyph[uni]
	gl=font[gly]
	lu=list()
	if len(glyph_codes[gly])<1:
		if gl.unicode==uni:
			gl.unicode=-1
			return
		gl.unicode=-1
		if gl.altuni!=None:
			lu=list()
			for alt in gl.altuni:
				if alt[1] > 0:
					lu.append(alt)
	else:
		gl.unicode=glyph_codes[gly][0]
		lu=list()
		if gl.altuni!=None:
			lu=list()
			for alt in gl.altuni:
				if alt[1] > 0:
					lu.append(alt)
		for u1 in glyph_codes[gly][1:]:
			lu.append((u1, -1, 0))
	if len(lu) > 0:
		gl.altuni = tuple(lu)
	else:
		gl.altuni = None

def adduni(gly, uni):
	glyph_codes[gly].append(uni)
	code_glyph[uni]=gly
	if font[gly].unicode<0:
		font[gly].unicode=uni
	else:
		lu=list()
		if font[gly].altuni != None:
			for alt in font[gly].altuni:
				lu.append(alt)
		lu.append((uni, -1, 0))
		font[gly].altuni = tuple(lu)

def stlookups():
	font.addLookup('stchar', 'gsub_single', (), (("ccmp",(("hani",("dflt")),)),))
	font.addLookup('stchar1', 'gsub_single', (), ())
	font.addLookup('stchar2', 'gsub_single', (), ())
	font.addLookup('stchar3', 'gsub_single', (), ())
	font.addLookup('stchar4', 'gsub_single', (), ())
	font.addLookupSubtable('stchar', 'sttab')
	font.addLookupSubtable('stchar1', 'sttab1')
	font.addLookupSubtable('stchar2', 'sttab2')
	font.addLookupSubtable('stchar3', 'sttab3')
	font.addLookupSubtable('stchar4', 'sttab4')
	with open(os.path.join(pydir, 'stoneo.dt'), 'r', encoding = 'utf-8') as f:
		for line in f.readlines():
			line = line.strip()
			if line.startswith('#') or '-' not in line:
				continue
			s, t = line.strip().split(' ')[0].split('-')
			s = s.strip()
			t = t.strip()
			if s and t and s != t and ord(t) in code_glyph and ord(s) in code_glyph:
				gntc = code_glyph[ord(t)]
				gnsc = code_glyph[ord(s)]
				if gntc != gnsc:
					font[gnsc].addPosSub('sttab', gntc)
	font.addLookup('stdict', 'gsub_contextchain', (), (("ccmp",(("hani",("dflt")),)),))
	with open(os.path.join(pydir, 'stonem.dt'),'r',encoding = 'utf-8') as f:
		sig1=set()
		sig2=set()
		sig3=set()
		sig4=set()
		ltc=dict()
		i=1
		linesrv=f.readlines()
		linesrv.reverse()
		for line in linesrv:
			if line.strip().startswith('#') or '-' not in line:
				continue
			ls=line.strip().split(' ')
			s, t=ls[0].split('-')
			dics=ls[1:]
			sg=code_glyph[ord(s)]
			tg=code_glyph[ord(t)]
			if sg!=tg and tg not in ltc:
				if sg not in sig1:
					sig1.add(sg)
					font[sg].addPosSub('sttab1', tg)
					ltc[tg]='stchar1'
				elif sg not in sig2:
					sig2.add(sg)
					font[sg].addPosSub('sttab2', tg)
					ltc[tg]='stchar2'
				elif sg not in sig3:
					sig3.add(sg)
					font[sg].addPosSub('sttab3', tg)
					ltc[tg]='stchar3'
				elif sg not in sig4:
					sig4.add(sg)
					font[sg].addPosSub('sttab4', tg)
					ltc[tg]='stchar4'
			mt=list()
			chat=-1
			for strs in dics:
				lw=list()
				if len(strs)==1 and strs[0]==s:
					chat=dics.index(strs)
				for ch in strs:
					codch=ord(ch)
					if codch in code_glyph:
						if code_glyph[codch] not in lw:
							lw.append(code_glyph[codch])
						else:
							print('Skip', ch)
				if len(lw)>0:
					lw1=f'[{" ".join(lw)}]'
					mt.append(lw1)
				else:
					break
			if not (s and t) or chat<0:
				raise RuntimeError(line)
			sb=str()
			lkp=''
			if tg in ltc:
				lkp=f' @<{ltc[tg]}>'
			noch=True
			for m1 in mt:
				if mt.index(m1)==chat and noch:
					sb+='| '+m1+f'{lkp} | '
					noch=False
				else:
					sb+=m1+f' '
			font.addContextualSubtable(
				lookup='stdict',
				subtable='ldict'+str(i),
				type='coverage',
				rule=sb)
			i+=1

def stname():
	sfntnames=list(font.sfnt_names)
	sfntnames2=list()
	for nt in sfntnames:
		nn=list(nt)
		nn[2]=nn[2].replace('Classic', 'T').replace('Old', 'T').replace('ODict', 'T').replace('华英明朝', '華英明朝').replace('传承体', '繁體').replace('傳承體', '繁體').replace('旧印体', '繁體').replace('舊印體', '繁體').replace('旧典体', '繁體').replace('舊典體', '繁體')
		nt=tuple(nn)
		sfntnames2.append(nt)
	font.sfnt_names=tuple(sfntnames2)

print('====Start Build HuayingMincho Fonts====\n')
inf=str()
outf=str()
style=str()
if len(sys.argv)>2 and os.path.isfile(sys.argv[1]):
	inf=sys.argv[1]
	outf=sys.argv[2]
else:
	while not os.path.isfile(inf):
		inf=input('请输入字体文件路径（或拖入文件）：\n')
		inf=ckfile(inf)
		if not os.path.isfile(inf):
			print('文件不存在，请重新选择！\n')
	while not outf.strip():
		outf=input('请输入输出文件：\n')
if len(sys.argv)>3 and sys.argv[3] in ('1', '2', '3'):
	style=sys.argv[3]
else:
	while style not in ('1', '2', '3'):
		style=input('请选择字形变体参考对象：\n\t1.旧印刷体，新细明体\n\t2.传承旧字\n\t3.康熙字典\n')

print('Loading font...')
font = fontforge.open(inf)
if font.is_cid:
	print('Warning: this is a CID font, we need to FLATTEN it!')
	font.cidFlatten()
font.reencode("unicodefull")
tv=dict()
ltb=list()
mvar=dict()
vtb=list()
exch=set()
mulch=list()
with open(os.path.join(pydir, 'mulcodechar.txt'), 'r', encoding='utf-8') as f:
	for line in f.readlines():
		line=line.strip()
		if line.startswith('#'):
			continue
		a=line.split('\t')
		exch.add(a[0])
		mulch.append((a[0], a[1]))
with open(os.path.join(pydir, 'mulcodevar.txt'), 'r', encoding='utf-8') as f:
	for line in f.readlines():
		line=line.strip()
		if line.startswith('#'):
			continue
		a=line.split('\t')
		if style=='3' and a[0]=='即':
			continue
		tv[ord(a[1])]=int(a[3].split(' ')[1].strip(), 16)
		mvar[ord(a[1])]=(int(a[2].split(' ')[1].strip(), 16), ord(a[0]))
		exch.add(a[0])
with open(os.path.join(pydir, 'uvs-get-MARK-0'+style+'.txt'), 'r', encoding='utf-8') as f:
	for line in f.readlines():
		line=line.strip()
		if line.startswith('#'):
			continue
		if line.endswith('X'):
			a=line.split(' ')
			if a[0] not in exch:
				tv[ord(a[0])]=int(a[3].strip('X').strip(), 16)

for gls in font.glyphs():
	if gls.altuni!=None:
		for alt in gls.altuni:
			if alt[1]>0:
				if alt[0] in mvar and alt[1]==mvar[alt[0]][0]:
					vtb.append((gls.glyphname, mvar[alt[0]][1]))
				if alt[0] in tv and tv[alt[0]]==alt[1]:
					ltb.append((gls.glyphname, alt[0]))
print('Moving codes...')

code_glyph = dict()
glyph_codes=dict()
getallcodesname(font, code_glyph, glyph_codes)

for v1 in vtb:
	addglyuni(v1[0], v1[1])

for t1 in ltb:
	unimvtogly(t1[1], t1[0])

print('Checking multicode...')
for chd in mulch:
	mvcodetocode(ord(chd[0]), ord(chd[1]))

print('Checking variants...')
addvariants()

print('Setting font info...')
font.os2_vendor='GWF '
sfntnames=list(font.sfnt_names)
for jn in sfntnames:
	if jn[0]=='Japanese':
		for lan in ['Chinese (Taiwan)', 'Chinese (PRC)', 'Chinese (Hong Kong)', 'Chinese (Macau)']:
			n1=list(jn)
			n1[0]=lan
			sfntnames.append(tuple(n1))
sfntnames2=list()
if style=='1':
	fontname+=' Old'
	tcname+=' 舊印體'
	scname+=' 旧印体'
elif style=='2':
	fontname+=' Classic'
	tcname+=' 傳承體'
	scname+=' 传承体'
elif style=='3':
	fontname+=' ODict'
	tcname+=' 舊典體'
	scname+=' 旧典体'
for nt in sfntnames:
	nn=list(nt)
	#if nn[0]=='Japanese':
	#	continue
	nn[2]=nn[2].replace('IPAmjMincho', fontname).replace('Version 006.01', 'Version '+fontver)
	if nn[0]=='Chinese (PRC)':
		nn[2]=nn[2].replace('IPAmj明朝', scname)
	else:
		nn[2]=nn[2].replace('IPAmj明朝', tcname)
	if nn[1]=='PostScriptName':
		nn[2]=nn[2].replace(' ', '')
	if nn[1]=='Copyright':
		nn[2]='Copyright(c) HuayingMincho, 2022. You must accept "https://opensource.org/licenses/IPA/" to use this product.'
	nt=tuple(nn)
	sfntnames2.append(nt)
sfntnames2.append(('English (US)', 'Vendor URL', vendorURL))
font.sfnt_names=tuple(sfntnames2)
font.sfntRevision = float(fontver)
del tv
print('Generating font(s)...')
if len(sys.argv)>4 and sys.argv[4].lower()=='t' and os.path.isdir(outf):
	defn=['HuayingMinchoOld', 'HuayingMinchoClassic', 'HuayingMinchoODict']
	oft=os.path.join(outf, defn[int(style)-1]+'.ttf')
	oftst=os.path.join(outf, 'HuayingMinchoT.ttf')
	font.generate(oft)
	print('Convert to TC...')
	stlookups()
	stname()
	font.generate(oftst)
else:
	font.generate(outf)
print('Finished!')
