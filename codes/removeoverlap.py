import sys
import fontforge
print('Loading')
font=fontforge.open(sys.argv[1])
print('Removing Overlap')
font.selection.all()
font.removeOverlap()
print('Saving')
font.generate(sys.argv[2])
print('Done')