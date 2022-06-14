
import opt.EvaluationFunction;
import shared.Instance;
import util.linalg.DenseVector;
import util.linalg.Vector;

/**
 * A function that returns value according to following pseudo-code
 *
 *   given a string, s, of length N, some T < N/2
 *   tail0 ? number of consecutive 0's at end of string
 *   head1 ? number of consecutive 1's at beginning of string
 *   R ? N if (tail0 > T and head1 > T)
 *   R ? 0 otherwise
 *   return max(tail0, head1) + R
 *
 * @author Jonathan Hudgins jhudgins8@gatech.edu
 * @version 1.0
 */
public class FourPeaksEvaluation implements EvaluationFunction {

    private int T;
    private int N;

    private int tail0(Vector data) {
        int count = 0;
        int i = data.size() - 1;
        while (i >= 0 && data.get(i)==0) {
            count++;
            i--;
        }
        return count;
    }

    private int head1(Vector data) {
        int count = 0;
        int i = 0;
        while (i < data.size() && data.get(i)==1) {
            count++;
            i++;
        }
        return count;
    }

    public FourPeaksEvaluation(int N, int T) {
        this.N = N;
        this.T = T;
    }

    /**
     * @see opt.EvaluationFunction#value(opt.OptimizationData)
     */
    public double value(Instance d) {
        Vector data = d.getData();
        int tail = tail0(data);
        int head = head1(data);
        int R = (tail > T && head > T) ? N : 0;
        return Math.max(tail, head) + R;
    }

    public int max(int N) {
        Vector v = new DenseVector(N);
        for (int i=0 ; i<T+1; i++) {
            v.set(i, 1);
        }
        for (int i=T+1; i<N; i++) {
            v.set(i, 0);
        }
        Instance instance = new Instance(v);
        return (int)value(instance);
    }
}
