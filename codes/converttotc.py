import os, sys, fontforge
from itertools import chain

pydir = os.path.abspath(os.path.dirname(__file__))

#fontver='1.000'
#fontname='HuayingMincho'
#cnname='華英明朝'
#cnsname='华英明朝'
#vendorURL='https://github.com/HuayingMincho'

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

def transforme(tabch):
	with open(os.path.join(pydir, f'datas/Chars_{tabch}.txt'), 'r',encoding = 'utf-8') as f:
		for line in f.readlines():
			line = line.strip()
			if line.startswith('#') or '\t' not in line:
				continue
			s, t = line.strip().split('\t')
			s = s.strip()
			t = t.strip()
			if s and t and s != t and (usemulchar or not s in mulchar):
				mvcodetocode(ord(s), ord(t))

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

def removeglyhps():
	alcodes = set(chain(
		range(0x0000, 0x007E + 1),
		range(0x02B0, 0x02FF + 1),
		range(0x2002, 0x203B + 1),
		range(0x2E00, 0x2E7F + 1),
		range(0x2E80, 0x2EFF + 1),
		range(0x3000, 0x301C + 1),
		range(0x3100, 0x312F + 1),
		range(0x3190, 0x31BF + 1),
		range(0xFE10, 0xFE1F + 1),
		range(0xFE30, 0xFE4F + 1),
		range(0xFF01, 0xFF5E + 1),
		range(0xFF5F, 0xFF65 + 1),
	))
	with open(os.path.join(pydir, 'datas/Hans.txt'), 'r', encoding = 'utf-8') as f:
		for line in f.readlines():
			if line.strip() and not line.strip().startswith('#'):
				alcodes.add(ord(line.strip()))
	useg=set()
	for gls in font.glyphs():
		if gls.glyphname in ('.notdef', '.null', 'nonmarkingreturn', 'NULL', 'NUL'):
			useg.add(gls.glyphname)
		elif len(set(glyph_codes[gls.glyphname]).intersection(alcodes)) > 0:
			useg.add(gls.glyphname)
	reget = set()
	for gly in useg:
		tg = font[gly].getPosSub('*')
		if len(tg) > 0:
			for t1 in tg:
				if t1[1] == 'Substitution' and t1[2] not in useg:
					reget.add(t1[2])
	useg.update(reget)
	for gls in font.glyphs():
		if gls.glyphname not in useg:
			font.removeGlyph(gls)
	getallcodesname(font, code_glyph, glyph_codes)

def ForCharslookups():
	font.addLookup('stchar', 'gsub_single', (), (("liga",(("hani",("dflt")),)),))
	font.addLookupSubtable('stchar', 'stchar1')
	tabch='tct'
	with open(os.path.join(pydir, f'datas/Chars_{tabch}.txt'), 'r', encoding = 'utf-8') as f:
		for line in f.readlines():
			line = line.strip()
			if line.startswith('#') or '\t' not in line:
				continue
			s, t = line.strip().split('\t')
			s = s.strip()
			t = t.strip()
			if s and t and s != t and s in mulchar:
				addlookupschar(ord(t), ord(s))
	with open(os.path.join(pydir, 'datas/Punctuation.txt'), 'r',encoding = 'utf-8') as f:
		for line in f.readlines():
			line = line.strip()
			if line.startswith('#') or '\t' not in line:
				continue
			s, t = line.strip().split('\t')
			s = s.strip()
			t = t.strip()
			if s and t and s != t:
				addlookupschar(ord(t), ord(s))

def addlookupschar(tcunic, scunic):
	if tcunic in code_glyph and scunic in code_glyph:
		gntc = code_glyph[tcunic]
		gnsc = code_glyph[scunic]
		if gntc != gnsc:
			font[gnsc].addPosSub('stchar1', gntc)

def ForWordslookups():
	stword = list()
	with open(os.path.join(pydir, 'datas/STPhrases.txt'),'r',encoding = 'utf-8') as f:
		for line in f.readlines():
			line = line.strip()
			if line.startswith('#') or '\t' not in line:
				continue
			isavail = True
			for ch1 in line.strip().replace('\t', '').replace(' ', ''):
				if ord(ch1) not in code_glyph:
					isavail = False
					break
			if isavail:
				s, t = line.strip().split(' ')[0].split('\t')
				if s.strip() and t.strip():
					stword.append((s.strip(), t.strip()))
	if len(stword) < 1:
		return
	sumf = sum(1 for _ in font.glyphs())
	if len(stword) + sumf > 65535:
		raise RuntimeError('Not enough glyph space! You need ' + str(len(stword) + sumf - 65535) + ' more glyph space!')
	stword.sort(key=lambda x:len(x[0]), reverse = True)
	font.addLookup('stmult', 'gsub_multiple', (), (("liga",(("hani",("dflt")),)),), 'stchar')
	font.addLookup('stliga', 'gsub_ligature', (), (("liga",(("hani",("dflt")),)),))
	i, j, tlen, wlen = 0, 0, 0, len(stword[0][0])
	font.addLookupSubtable('stmult', 'stmult0')
	font.addLookupSubtable('stliga', 'stliga0')
	for wd in stword:
		tlen += len(wd[0] + wd[1])
		wlen2 = len(stword[i][0])
		if tlen >= 15000 or wlen2 < wlen:
			tlen = 0
			wlen = wlen2
			j += 1
			font.addLookupSubtable('stmult', 'stmult' + str(j), 'stmult' + str(j - 1))
			font.addLookupSubtable('stliga', 'stliga' + str(j), 'stliga' + str(j - 1))
		i += 1
		addlookupsword(wd[1], wd[0], str(j), str(i))

def addlookupsword(tcword, scword, j, i):
	newgname = 'ligast' + i
	wdin = list()
	wdout = list()
	for s1 in scword:
		try:
			glys = font[code_glyph[ord(s1)]]
		except TypeError:
			print('Skip ' + s1)
			return
		wdin.append(glys.glyphname)
	for t1 in tcword:
		try:
			glyt = font[code_glyph[ord(t1)]]
		except TypeError:
			print('Skip ' + t1)
			return
		wdout.append(glyt.glyphname)
	newg = font.createChar(-1, newgname)
	newg.width = 1000
	newg.vwidth = 800
	newg.addPosSub('stliga' + j, tuple(wdin))
	newg.addPosSub('stmult' + j, tuple(wdout))

inf=str()
outf=str()
print('====生成华英明朝 繁体====\n')
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
style=str()
if len(sys.argv)>3 and sys.argv[3] in ('1', '2'):
	style=sys.argv[3]
else:
	while style not in ('1', '2'):
		style=input('请选择繁体类型：\n\t1.普通\n\t2.可处理简繁一对多\n')

def getmulchar(allch):
	s = str()
	with open(os.path.join(pydir, 'datas/Multi.txt'), 'r', encoding = 'utf-8') as f:
		for line in f.readlines():
			line = line.strip()
			if not line or line.startswith('##'):
				continue
			if allch:
				s += line.strip('#').strip()
			elif not line.startswith('#'):
				s += line
	return s

print('正在载入字体...')
font = fontforge.open(inf)
if font.is_cid:
	print('Warning: this is a CID font, we need to FLATTEN it!')
	font.cidFlatten()
font.reencode("unicodefull")
print('正在检查代码点...')
code_glyph = dict()
glyph_codes=dict()
getallcodesname(font, code_glyph, glyph_codes)
print('正在检查异体字...')
addvariants()
print('正在移动代码点...')
usemulchar = style=='1'
mulchar = getmulchar(style=='2')
transforme('tct')
print('正在移除字形...')
removeglyhps()
print('正在检查额外异体字...')
addvariants()
print('处理 GSUB...')
print('正在添加单字替换表...')
ForCharslookups()
print('正在添加多字替换表...')
ForWordslookups()

print('正在设置字体名称...')
sfntnames=list(font.sfnt_names)
sfntnames2=list()
for nt in sfntnames:
	nn=list(nt)
	nn[2]=nn[2].replace('Classic', 'T').replace('Old', 'T').replace('ODict', 'T').replace('华英明朝', '華英明朝').replace('传承体', '繁體').replace('傳承體', '繁體').replace('旧印体', '繁體').replace('舊印體', '繁體').replace('旧典体', '繁體').replace('舊典體', '繁體')
	#if nn[1]=='PostScriptName':
	#	nn[2]=nn[2].replace(' ', '')
	nt=tuple(nn)
	sfntnames2.append(nt)
font.sfnt_names=tuple(sfntnames2)
print('正在补全字库...')
code_glyph = dict()
glyph_codes=dict()
getallcodesname(font, code_glyph, glyph_codes)
addvariants()
print('正在生成字体...')
font.generate(outf)
print('完成!')

