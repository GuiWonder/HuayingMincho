import os
from shutil import copy, copytree, rmtree

os.system('git clone https://github.com/GuiWonder/TCFontCreator.git') 
rmtree('./codes/datas')
copytree('./TCFontCreator/main/datas', './codes/datas')
os.system('7z e ./codes/ipamjm00601/ipamjm.7z -o./')
os.system('fontforge -script ./codes/huayingmincho.py ./ipamjm.ttf ./HuayingMinchoOld.ttf 1')
os.system('fontforge -script ./codes/huayingmincho.py ./ipamjm.ttf ./HuayingMinchoClassic.ttf 2')
os.system('fontforge -script ./codes/huayingmincho.py ./ipamjm.ttf ./HuayingMinchoODict.ttf 3')
os.system('rm -f ./ipamjm.ttf')
os.system('fontforge -script ./codes/converttotc.py ./HuayingMinchoClassic.ttf ./HuayingMinchoT.ttf 2')
#os.system('fontforge -script ./codes/ttf2ttc.py ./HuayingMincho.ttc ./HuayingMinchoOld.ttf ./HuayingMinchoClassic.ttf ./HuayingMinchoODict.ttf')
os.system('python3 ./codes/otf2otc.py -o ./HuayingMincho.ttc ./HuayingMinchoOld.ttf ./HuayingMinchoClassic.ttf ./HuayingMinchoODict.ttf')

