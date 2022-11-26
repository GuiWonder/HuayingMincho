#!/bin/sh

# rm ./codes/datas/*
# wget -P ./codes/datas https://github.com/GuiWonder/TCFontCreator/raw/main/main/datas/Variants.txt || exit 1
wget -P src https://dforest.watch.impress.co.jp/library/i/ipamjfont/10750/ipamjm00601.zip || exit 1
7z e ./src/ipamjm00601.zip -o./src/
fontforge -script ./codes/huayingmincho.py ./src/ipamjm.ttf ./HuayingMinchoOld.ttf 1
#fontforge -script ./codes/huayingmincho.py ./src/ipamjm.ttf ./HuayingMinchoClassic.ttf 2
fontforge -script ./codes/huayingmincho.py ./src/ipamjm.ttf ./ 2 t
fontforge -script ./codes/huayingmincho.py ./src/ipamjm.ttf ./HuayingMinchoODict.ttf 3
rm -rf ./src
python3 ./codes/otf2otc.py -o ./HuayingMincho.ttc ./HuayingMinchoOld.ttf ./HuayingMinchoClassic.ttf ./HuayingMinchoODict.ttf ./HuayingMinchoT.ttf
7z a AllFonts.7z *.tt* LICENSE.txt -mx=9 -mfb=256 -md=256m
