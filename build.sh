#!/bin/sh

wget -P ./temp https://dforest.watch.impress.co.jp/library/i/ipamjfont/10750/ipamjm00601.zip
7z e ./temp/ipamjm00601.zip -o./temp/

python3 ./codes/check.py ./temp/check.ttf ./temp/ipamjm.ttf ./codes/src/subset.ttf
python3 ./codes/huayingmincho.py ./temp/check.ttf ./HuayingMinchoOld.ttf 1
#fontforge -script ./codes/huayingmincho.py ./temp/check.ttf ./HuayingMinchoClassic.ttf 2
python3 ./codes/huayingmincho.py ./temp/check.ttf ./ 2 t
python3 ./codes/huayingmincho.py ./temp/check.ttf ./HuayingMinchoODict.ttf 3
otf2otc -o ./HuayingMincho.ttc ./HuayingMinchoOld.ttf ./HuayingMinchoClassic.ttf ./HuayingMinchoODict.ttf ./HuayingMinchoT.ttf
7z a HuayingMincho.7z *.tt* LICENSE.txt -mx=9 -mfb=256 -md=256m

rm -rf ./temp
