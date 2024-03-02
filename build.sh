#!/bin/sh

wget -P ./temp https://dforest.watch.impress.co.jp/library/i/ipamjfont/10750/ipamjm00601.zip
7z e ./temp/ipamjm00601.zip -o./temp/

fontforge -script ./codes/merge.py ./temp/merge.ttf ./temp/ipamjm.ttf ./codes/src/subset.ttf

fontforge -script ./codes/huayingmincho.py ./temp/merge.ttf ./HuayingMinchoOld.ttf 1
#fontforge -script ./codes/huayingmincho.py ./temp/merge.ttf ./HuayingMinchoClassic.ttf 2
fontforge -script ./codes/huayingmincho.py ./temp/merge.ttf ./ 2 t
fontforge -script ./codes/huayingmincho.py ./temp/merge.ttf ./HuayingMinchoODict.ttf 3

python3 ./codes/otf2otc.py -o ./HuayingMincho.ttc ./HuayingMinchoOld.ttf ./HuayingMinchoClassic.ttf ./HuayingMinchoODict.ttf ./HuayingMinchoT.ttf
7z a AllFonts.7z *.tt* LICENSE.txt -mx=9 -mfb=256 -md=256m

rm -rf ./temp
