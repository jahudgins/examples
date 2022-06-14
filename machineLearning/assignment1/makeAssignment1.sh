rm -rf $WORK/assignment1/jhudgins8
mkdir -p $WORK/assignment1/jhudgins8
cp -r speech $WORK/assignment1/jhudgins8
cp -r parsedNBA $WORK/assignment1/jhudgins8
cp -r scripts $WORK/assignment1/jhudgins8
cp README.txt $WORK/assignment1/jhudgins8
cp report.pdf $WORK/assignment1/jhudgins8/jhudgins8-analysis.pdf

# don't include nba data
rm jhudgins8/parsedNBA/*.arff

cd $WORK/assignment1
rm -f jhudgins8-extra.zip
zip jhudgins8-extra.zip jhudgins8/speech/*.arff
zip -r jhudgins8-extra.zip jhudgins8/speech/output
zip -r jhudgins8-extra.zip jhudgins8/parsedNBA/output
rm jhudgins8/speech/*.arff
rm -rf jhudgins8/speech/output
rm -rf jhudgins8/parsedNBA/output


rm -f jhudgins8.zip
zip -r jhudgins8.zip jhudgins8
