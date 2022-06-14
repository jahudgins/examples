echo parsing draft 2005
echo > ../rawdata/draft2005.csv;
for i in ../rawdata/draft2005/*;
do
    python draftScrub.py -f $i -s 2004-05 >> ../rawdata/draft2005.csv
done
echo

echo parsing draft 2006
echo > ../rawdata/draft2006.csv;
for i in ../rawdata/draft2006/*;
do
    python draftScrub.py -f $i -s 2005-06 >> ../rawdata/draft2006.csv
done
echo


echo parsing draft 2007
echo > ../rawdata/draft2007.csv;
for i in ../rawdata/draft2007/*;
do
    python draftScrub.py -f $i -s 2006-07 >> ../rawdata/draft2007.csv
done
echo


echo parsing draft 2008
echo > ../rawdata/draft2008.csv;
for i in ../rawdata/draft2008/*;
do
    python draftScrub.py -f $i -s 2007-08 >> ../rawdata/draft2008.csv
done
echo







