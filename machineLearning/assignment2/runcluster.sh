#!bash
export mycp="d:\svn\georgiatech\machineLearning\assignment2\bin;d:\github\ABAGAIL\bin" 
java -classpath $mycp Cluster --trainingfile data/isolet113Training.arff --testfile data/isolet113Test.arff --outdir svnignore/output/cluster
