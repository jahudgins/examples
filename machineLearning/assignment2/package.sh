mkdir -p ../../submissions/cs7641/assignment2/jhudgins8/bin
cp ../../../../github/ABAGAIL/ABAGAIL.jar ../../submissions/cs7641/assignment2/jhudgins8/bin
(cd bin; jar cvf ../assignment2.jar *)
cp assignment2.jar ../../submissions/cs7641/assignment2/jhudgins8/bin
robocopy /S ../../../../github/ABAGAIL/src ../../submissions/cs7641/assignment2/jhudgins8/ABAGAIL/src
robocopy /S src ../../submissions/cs7641/assignment2/jhudgins8/src
cp report/analysis.pdf ../../submissions/cs7641/assignment2/jhudgins8/jhudgins8-analysis.pdf
