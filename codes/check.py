import sys
from fontTools.ttLib import TTFont

outfile, infile, subft=sys.argv[1], sys.argv[2], sys.argv[3]

font=TTFont(infile)
font2=TTFont(subft)

cmap=font.getBestCmap()
cmap2=font2.getBestCmap()
go=font.getGlyphOrder()
uvg=set()
for table in font['cmap'].tables:
	if table.format==14:
		for vsl in table.uvsDict.keys():
			for cg in table.uvsDict[vsl]:
				if cg[1]==None: uvg.add(cmap[cg[0]])
				else: uvg.add(cg[1])

newgo=list(go)
for cd in cmap2.keys():
	g2=cmap2[cd]
	if g2 in ['.notdef', '.null', 'nonmarkingreturn', 'space']:
		continue
	if cd in cmap.keys() and cmap[cd] not in uvg:
		print('Replace', chr(cd))
		g1=cmap[cd]
		font['glyf'].glyphs[g1]=font2['glyf'].glyphs[g2]
		font['hmtx'][g1]=font2['hmtx'][g2]
		font['vmtx'][g1]=font2['vmtx'][g2]
	else:
		newg=g2
		j=1
		while newg in newgo:
			newg=g2+'.'+str(j)
			j+=1
		newgo.append(newg)
		for table in font['cmap'].tables:
			if (table.format==4 and cd<=0xFFFF) or table.format==12:
				print('Mapping', chr(cd))
				table.cmap[cd]=newg
		font['glyf'].glyphs[newg]=font2['glyf'].glyphs[g2]
		font['hmtx'][newg]=font2['hmtx'][g2]
		font['vmtx'][newg]=font2['vmtx'][g2]

print('Process GlyphOrder')
font.setGlyphOrder(newgo)

if font['post'].formatType!=3:
	try:
		print('Check post')
		font['maxp'].compile(font)
		font['post'].compile(font)
	except OverflowError:
		font['post'].formatType=3
		print("Warning: Dropping glyph names, they do not fit in 'post' table.")
for glyph in font['glyf'].glyphs.values():
	glyph.removeHinting()

print('Save', outfile)
font.save(outfile)

print('End')

