#!bash

#for pop in 100 200 400 800;
#do
#    for keepRatio in 0.01 0.02 0.04 0.10 0.20 0.40 0.60 0.70 0.80 0.90
#    do
#        export i="p$pop-k$keepRatio"
#        #mkdir -p svnignore/output/substring$i
#        #java -classpath "D:\svn\georgiatech\machineLearning\assignment2\bin;D:\github\ABAGAIL\bin" ComplimentSubstring --outdir svnignore/output/substring$i --length 20 --population $pop --evaluations 50000 --keepratio $keepRatio
#        python python/substringpop.py --population $pop --keepratio $keepRatio
#        # mkdir -p svnignore/plots/substring$i
#        # /c/Python27/python python/plotsubstring.py --plots svnignore/plots/substring$i --directory svnignore/output/substring$i
#    done
#done


for i in 15 20 25 30 35 40 45 50 55 60
do
#    mkdir -p svnignore/output/substring-length$i
#    java -classpath "D:\svn\georgiatech\machineLearning\assignment2\bin;D:\github\ABAGAIL\bin" ComplimentSubstring --outdir svnignore/output/substring-length$i --length $i --evaluations 50000
#    mkdir -p svnignore/plots/substring-length$i
    /c/Python27/python python/plotsubstring.py --plots svnignore/plots/substring-length$i --directory svnignore/output/substring-length$i
done


#for i in 2 4 8 16 32 64 128 256
#do
#    export dir="substringsa3"
#    mkdir -p svnignore/output/$dir
#    mkdir -p svnignore/plots/$dir
#    java -classpath "D:\svn\georgiatech\machineLearning\assignment2\bin;D:\github\ABAGAIL\bin" ComplimentSubstring --outdir svnignore/output/$dir --length 20 --evaluations 50000 --temponly $i
#    #/c/Python27/python python/plotsubstring.py --plots svnignore/plots/substring$i --directory svnignore/output/substring$i
#
#    # /c/Python27/python python/plotsubstring.py --plots svnignore/plots/substring15 --directory svnignore/output/substring15
#done

# mkdir -p svnignore/output/substring20
# java -classpath "D:\svn\georgiatech\machineLearning\assignment2\bin;D:\github\ABAGAIL\bin" ComplimentSubstring --outdir svnignore/output/substring20 --length 20  --evaluations 50000
# mkdir -p svnignore/plots/substring20
# /c/Python27/python python/plotsubstring.py --plots svnignore/plots/substring20 --directory svnignore/output/substring20

