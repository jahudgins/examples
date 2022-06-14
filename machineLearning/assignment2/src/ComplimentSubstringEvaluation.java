
import opt.EvaluationFunction;
import shared.Instance;
import util.linalg.DenseVector;
import util.linalg.Vector;

/**
 * A function that counts matches of the compliment of each substring starting at index 0
 * @author Jonathan Hudgins jhudgins8@gatech.edu
 * @version 1.0
 */
public class ComplimentSubstringEvaluation implements EvaluationFunction {
    /**
     * Count the number of times a set of substrings occur. The set of substrings
     * are the compliment of all possible strings starting at index 0 until length of
     * string.
     *
     * For instance:
     *      string: 00110
     *      substring set [1, 11, 110, 1100, 11001] (compliment of 0, 00, 001, 0011, and 00110)
     *      count: 2 + 1 + 1 + 0 + 0 = 4
     *
     * @see opt.EvaluationFunction#value(opt.OptimizationData)
     */
    public double value(Instance d) {
        Vector data = d.getData();
        double val = 0;
        for (int i = 0; i < data.size(); i++) {
            for (int j = 0; j < data.size()-i; j++) {
                if (complimentEquals(data, i+1, j)) {
                    val++;
                }
            }
        }
        return val;
    }

    private boolean complimentEquals(Vector data, int endBase, int startCmp) {
        for (int i=0; i<endBase; i++) {
           if (data.get(i) == data.get(startCmp + i)) {
              return false;
           }
        }
        return true;
    }

    private boolean incrementVector(Vector v) {
        for (int i=0; i<v.size(); i++) {
            if (v.get(i) == 0) {
                v.set(i, 1);
                return true; 
            }
            else {
                v.set(i, 0);
            }
        }
        return false;
    }

    public int max(int N) {
        Vector v = new DenseVector(N);
        for (int i=0 ; i<N; i+=2) {
            v.set(i, 1);
        }
        Instance instance = new Instance(v);
        return (int)value(instance);
    }
}
