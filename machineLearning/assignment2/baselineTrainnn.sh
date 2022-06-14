

for i in 1e-1 1e-2 1e-3 1e-4 1e-5 1e-6 1e-7 1e-8 1e-9
do
    mkdir svnignore/output/trainnnBaseline$i
    java -classpath "d:\svn\georgiatech\machineLearning\assignment2\bin;d:\github\ABAGAIL\bin" TrainNeuralNet --trainingfile data/isolet20Training.arff --testfile data/isolet20Test.arff --evaluations 100 --outdir svnignore/output/trainnnBaseline$i --baseline $i
done
