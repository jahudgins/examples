#jdb -launch \
java \
    DecisionTree \
    CLASSIFIER weka.classifiers.trees.J48 -U \
    FILTER weka.filters.unsupervised.instance.Randomize \
    DATASET testdata.arff
    # DATASET ../../speech/isolet5.arff
    # -classpath "c:/Program Files (x86)/Weka-3-6/weka.jar;." WekaDemo \
