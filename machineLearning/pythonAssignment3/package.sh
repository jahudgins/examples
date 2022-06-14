DEST=../../submissions/cs7641/assignment3/jhudgins8

rm -rf $DEST

mkdir -p $DEST
cp *.py $DEST
cp report/analysis.pdf $DEST/jhudgins8-analysis.pdf
cp README.txt $DEST/README.txt

mkdir -p $DEST/output
cp output/basketball.*.utilities $DEST/output
cp output/basketball.*.utilities $DEST/output
cp output/basketball.4level.optimal.png $DEST/output
cp output/buyCar18monthsNoSalvage.png $DEST/output
cp output/buyCar36months.png $DEST/output
cp output/buyCarRepair2000.png $DEST/output
cp output/basketball.optimalonly.png $DEST/output

cd $DEST/..
rm jhudgins8.zip
zip -r jhudgins8.zip jhudgins8

rm -rf jhudgins8
