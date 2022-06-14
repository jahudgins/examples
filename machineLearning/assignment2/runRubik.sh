#!bash

#for i in 1 2 3 4 5 6 7 8 9 10;
#do
#    mkdir -p output/rubiks$i
#    java -classpath "D:\svn\georgiatech\machineLearning\assignment2\bin;D:\github\ABAGAIL\bin" RubiksCube --outdir output/rubiks$i --moves 8 --evaluations 10000
#done

java -classpath "D:\svn\georgiatech\machineLearning\assignment2\bin;D:\github\ABAGAIL\bin" RubiksCube --outdir output/rubiksMassive --moves 20 --evaluations 10000000
