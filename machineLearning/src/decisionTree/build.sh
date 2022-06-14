# CLASSPATH needs to include "." and "weka.jar"

#javac DecisionTree.java 2>&1 | tee $WORK/javac.txt
#javac -g DecisionTree 2>&1 | tee $WORK/javac.txt
echo "javac -g `cygpath -a -m .`/DecisionTree.java 2>&1 | tee $WORK/javac.txt"
javac -g `cygpath -a -m .`/DecisionTree.java 2>&1 | tee $WORK/javac.txt
# javac DecisionTree
