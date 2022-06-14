import opt.EvaluationFunction;
import opt.OptimizationAlgorithm;
import shared.Instance;
import util.PythonOut;
import util.linalg.DenseVector;
import util.linalg.Vector;

/**
 * Count maximum
 *
 * Modified from ABAGAIL distribution: CountOnesTest.java
 *
 * @author Jonathan Hudgins
 * @version 1.0
 */

public class UtilTrain {
    public static void trainFixedEvaluations(OptimizationAlgorithm oa, int maxEvaluations) {
        int evaluations = 0;
        int iterations = 0;
        PythonOut.write(PythonOut.prefix+"['trainlabels'] = ['iterations','evaluations','bestvalue','bestoptimal','bbestinstance']\n");
        PythonOut.write(PythonOut.prefix+"['train'] = [\n");

        int printSamples = 1000;
        int printStep = maxEvaluations / printSamples;
        int printCount = 0;

        // limit number of evaluations instead of iterations
        while (evaluations < maxEvaluations) {
            oa.train();
            evaluations = oa.getEvaluations();

            // print stats after each printStep increment is crossed
            if (evaluations > (printCount + 1) * printStep) {
                printCount++;

                // get instance and value
                Instance bestInstance = oa.getOptimal();
                double bestValue = oa.getOptimizationProblem().value(bestInstance);
                double bestOptimumVal = oa.getBestOptimalValue();

                // format binary instance
                StringBuilder binary = new StringBuilder();
                binary.append("'0b");
                for (int i=0; i<bestInstance.size(); i++) {
                    binary.append(bestInstance.getDiscrete(i));
                }
                // too big for some values
                // int hexInstance = Integer.parseInt(binary.toString().substring(3), 2);
                // String hexString = "'0x" + Integer.toHexString(hexInstance) + "'";
                binary.append("'");

                // write 
                PythonOut.write("  [" + iterations+"," + evaluations+"," + bestValue+"," + bestOptimumVal+"," + binary+"],\n");
                // PythonOut.write("  [" + iterations+"," + evaluations+"," + bestValue+"," + binary+"," + hexString+"],\n");
            }
            iterations++;
        }
        PythonOut.write("]\n");
    }

    public static void trainUntilMax(OptimizationAlgorithm oa, double maxValue, int maxEvaluations, int printStep) {
        int evaluations = 0;
        int iterations = 0;
        PythonOut.write(PythonOut.prefix+"['trainlabels'] = ['iterations','evaluations','bestvalue','bestoptimal','bbestinstance']\n");
        PythonOut.write(PythonOut.prefix+"['train'] = [\n");

        int printCount = 0;
        double bestValue = -Double.MAX_VALUE;

        // limit number of evaluations instead of iterations
        while (bestValue < maxValue) {
            if (maxEvaluations > 0 && evaluations > maxEvaluations) {
                break;
            }
            oa.train();
            Instance bestInstance = oa.getOptimal();
            bestValue = oa.getOptimizationProblem().value(bestInstance);
            evaluations = oa.getEvaluations();

            // print stats after each printStep increment is crossed
            if (bestValue == maxValue || evaluations > (printCount + 1) * printStep) {
                printCount++;

                // get instance and value
                double bestOptimumVal = oa.getBestOptimalValue();

                // format binary instance
                StringBuilder binary = new StringBuilder();
                binary.append("'0b");
                for (int i=0; i<bestInstance.size(); i++) {
                    binary.append(bestInstance.getDiscrete(i));
                }
                // too big for some values
                // int hexInstance = Integer.parseInt(binary.toString().substring(3), 2);
                // String hexString = "'0x" + Integer.toHexString(hexInstance) + "'";
                binary.append("'");

                // write 
                PythonOut.write("  [" + iterations+"," + evaluations+"," + bestValue+"," + bestOptimumVal+"," + binary+"],\n");
                // PythonOut.write("  [" + iterations+"," + evaluations+"," + bestValue+"," + binary+"," + hexString+"],\n");
            }
            iterations++;
        }
        PythonOut.write("]\n");
        PythonOut.write("succeeded", (bestValue < maxValue) ? 0 : 1);
    }



    public static boolean incrementVector(Vector v) {
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

    public static int[] distribution(EvaluationFunction ef, int N) {
        // more than 20 will take too much memory and get stuck for way too long
        // so just return null and let the app get an exception
        if (N > 30) {
            return null;
        }
        int[] dist = new int[(int)Math.pow(2, N)];
        Vector v = new DenseVector(N);
        Instance instance = new Instance(v);
        int max = 0;
        int i = 0;
        while (true) {
            dist[i] = (int)ef.value(instance);
            if (!incrementVector(v)) {
                break;
            }
            i++;
        }
        return dist;
    }

    public static int findmax(EvaluationFunction ef, int N) {
        int max = 0;
        Vector v = new DenseVector(N);
        Instance instance = new Instance(v);
        while (true) {
            max = Math.max(max, (int)ef.value(instance));
            if (!incrementVector(v)) {
                break;
            }
        }
        return max;

    }
}
