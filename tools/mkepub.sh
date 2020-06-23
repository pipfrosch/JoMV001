#!/bin/bash

CWD=`pwd`

TMP=`mktemp -d /tmp/JOMV001.XXXXXXXX`

pushd ${TMP}

git clone https://github.com/pipfrosch/JoMV001.git
cd JoMV001
# Switch to Alpha2 branch
git checkout Alpha2

cd TheBook/EPUB

python3 ../../tools/updateTimestamp.py content.opf
#timestamp=`python3 ../../tools/getTimestamp.py content.opf`
python3 ../../tools/generateOPDS.py ${CWD}/foo.atom

cd fonts
rm -f .gitignore
cp -p /usr/local/ePubFonts/ClearSans-BoldItalic-wlatin.ttf .
cp -p /usr/local/ePubFonts/ClearSans-Bold-wlatin.ttf .
cp -p /usr/local/ePubFonts/ClearSans-Italic-wlatin.ttf .
cp -p /usr/local/ePubFonts/ClearSans-Regular-wlatin.ttf .
cp -p /usr/local/ePubFonts/ComicNeue-Bold-wlatin.otf .
cp -p /usr/local/ePubFonts/ComicNeue-Regular-wlatin.otf .
#cp -p /usr/local/ePubFonts/DancingScript-Regular.otf .
cp -p /usr/local/ePubFonts/FiraMono-Medium-wlatin.ttf .
cp -p /usr/local/ePubFonts/FiraMono-Bold-wlatin.ttf .
cd ../..

echo -n application/epub+zip >mimetype

zip -r -X Book.zip mimetype META-INF EPUB
mv Book.zip JoM-V001.kepub.epub

#dyslexia friendly version
find . -type f -print |grep "\.xhtml$" |while read file; do
  cat ${file} \
|sed -e s?"Æ"?"AE"?g \
|sed -e s?"æ"?"ae"?g \
|sed -e s?"Œ"?"OE"?g \
|sed -e s?"œ"?"oe"?g > tmp.sed
cat tmp.sed > ${file}
done
rm -f tmp.sed
cat EPUB/css/noitalics.css >> EPUB/css/a11y.css
zip -r -X Book.zip mimetype META-INF EPUB
mv Book.zip JoM-V001-noitalics.kepub.epub

# other versions here

sh ../tools/epubcheck.sh JoM-V001.kepub.epub

if hash ace 2>/dev/null; then
  if [ ! -f ${CWD}/AceReport/noace.tmp ]; then
    ace -f -s -o AceReport JoM-V001.kepub.epub
    rm -rf ${CWD}/AceReport/data
    [ ! -d ${CWD}/AceReport ] && mkdir ${CWD}/AceReport
    mv AceReport/data ${CWD}/AceReport/
    mv AceReport/report.html ${CWD}/AceReport/
    mv AceReport/report.json ${CWD}/AceReport/
    echo "Accessibility report written to AceReport directory"
    echo `pwd`
  fi
fi

mv JoM-V001.kepub.epub ${CWD}/opds/
mv JoM-V001-noitalics.kepub.epub ${CWD}/opds/

popd

if hash ace 2>/dev/null; then
  if [ -f AceReport/.gitignore ]; then
    if [ ! -f AceReport/noace.tmp ]; then
      git commit -m "update AceReport" AceReport/report.*
    fi
  fi
fi

rm -rf ${TMP}

exit 0

