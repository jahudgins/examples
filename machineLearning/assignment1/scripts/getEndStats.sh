for i in 1 2 3 4 5 6;
do
  for j in 12-13 11-12 10-11 09-10 08-09;
  do
    curl http://stats.nba.com/leaguePlayerGeneral.html?ls=iref%3Anba%3Agnav\&pageNo=$i\&rowsPerPage=100\&Season=20$j > ../rawdata/players.$j.$i.txt
  done
done
