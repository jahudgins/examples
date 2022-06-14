#!bash

export mycp="c:\svn\georgiatech\machineLearning\assignment2\bin;c:\github\ABAGAIL\bin"
for i in 10 15 20 25 30
do
    export dir=svnignore/output/fourpeaks-length$i.$1
    echo $dir
    mkdir -p $dir
    java -classpath $mycp FourPeaks --outdir $dir --length $i
    # mkdir -p svnignore/plots/substring-length$i
    #/c/Python27/python python/plotsubstring.py --plots svnignore/plots/substring-length$i --directory svnignore/output/substring-length$i
done

for i in 35 40 45 50 55 60
do
    export dir=svnignore/output/fourpeaks-length$i.$1
    echo $dir
    mkdir -p $dir
    java -classpath $mycp FourPeaks --outdir $dir --length $i --iterations 2000000
done
