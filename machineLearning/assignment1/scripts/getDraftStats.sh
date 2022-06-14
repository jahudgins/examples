for i in 8 7 6 5 4;
do
	mkdir -p ../rawdata/draft200$i
	for j in `cat ../rawdata/draft200$i.html`;
	do
		# echo curl http://www.nba.com/draft200$i/profiles/$j into ../rawdata/draft200$i/$j
		curl http://www.nba.com/draft200$i/profiles/$j > ../rawdata/draft200$i/$j
	done
done
