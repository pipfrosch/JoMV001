#!/bin/bash

function getfonts {
  GITDIR="$1"
  EPUBDIR="$2"
  pushd ${GITDIR}
  if [ ! -f fonts.sha256.txt ]; then
    echo "No fonts checksum"
    exit 1
  fi
  cat fonts.sha256.txt |cut -d' ' -f3 |while read fontfile; do
    if [ ! -f ${fontfile} ]; then
      curl -O https://misc.pipfrosch.com/ePubFonts/${fontfile}
    fi
  done
  popd
  pushd ${EPUBDIR}
  if [ ! -f fonts.sha256.txt ]; then
    echo "No fonts checksum"
    exit 1
  fi
  cat fonts.sha256.txt |cut -d' ' -f3 |while read fontfile; do
    cp -p ${GITDIR}/${fontfile} .
  done
  sha256sum -c fonts.sha256.txt
  if [ $? -ne 0 ]; then
    echo "Font checksum problem"
    exit 1;
  fi
  rm -f fonts.sha256.txt .gitignore
  popd
}

CWD=`pwd`

TMP=`mktemp -d /tmp/JOMV001.XXXXXXXX`

pushd ${TMP}

git clone https://github.com/pipfrosch/JoMV001.git
cd JoMV001
# Switch to Alpha2 branch
git checkout Alpha2

getfonts ${CWD}/TheBook/EPUB/fonts ${TMP}/JoMV001/TheBook/EPUB/fonts

cd TheBook/EPUB
python3 ../../tools/updateTimestamp.py content.opf
cd ../..

#generate atom file
pushd ${CWD}/opds
cat epub.json |sed -e s?"\.atom"?"-noitalics.atom"?g \
              |sed -e s?"\.kepub.epub"?"-noitalics.kepub.epub"?g \
              > epub-noitalics.json
popd


python3 tools/generateOPDS.py TheBook/EPUB/content.opf ${CWD}/opds/epub.json
python3 tools/generateOPDS.py TheBook/EPUB/content.opf ${CWD}/opds/epub-noitalics.json

cat opds/JoM-V001.atom > ${CWD}/opds/JoM-V001.atom
cat opds/JoM-V001-noitalics.atom > ${CWD}/opds/JoM-V001-noitalics.atom

rm -f ${CWD}/opds/epub-noitalics.json

cd TheBook

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

mv JoM-V001.kepub.epub ${CWD}/
mv JoM-V001-noitalics.kepub.epub ${CWD}/

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

