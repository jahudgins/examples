for i in 8 7 6 5 4;
do
	curl http://www.nba.com/draft200$i/profiles/byName.html > ../rawdata/draft200$i.html
done
