import java.util.Arrays;

import opt.DiscreteChangeOneNeighbor;
import opt.GenericHillClimbingProblem;
import opt.HillClimbingProblem;
import opt.NeighborFunction;
import opt.OptimizationAlgorithm;
import opt.SimulatedAnnealing;
import opt.ga.CrossoverFunction;
import opt.ga.DiscreteChangeOneMutation;
import opt.ga.GenericGeneticAlgorithmProblem;
import opt.ga.GeneticAlgorithmProblem;
import opt.ga.MutationFunction;
import opt.ga.SingleCrossOver;
import opt.ga.StandardGeneticAlgorithm;
import opt.ga.TwoPointCrossOver;
import opt.ga.UniformCrossOver;
import opt.prob.GenericProbabilisticOptimizationProblem;
import opt.prob.MIMIC;
import opt.prob.ProbabilisticOptimizationProblem;
import shared.Instance;
import util.PythonOut;
import util.linalg.DenseVector;
import util.linalg.Vector;
import dist.DiscreteDependencyTree;
import dist.DiscreteUniformDistribution;
import dist.Distribution;

/**
 * Count maximum
 *
 * Modified from ABAGAIL distribution: CountOnesTest.java
 *
 * @author Jonathan Hudgins
 * @version 1.0
 */

public class RubiksCube {
    /** The n value */
    private static int N = 3 * 3;
    private static int sEvaluations = 1000;
    private static String sOutDir = ".";

    private static void usage() {
        System.out.println("Usage: RubiksCube [options]");
        System.out.println("--help              print help");
        System.out.println("--moves <n>         <n> moves to scramble and solve");
        System.out.println("--evaluations <n>   run training for <n> evaluations");
        System.out.println("--outdir <dir>      diretory to output files");
    }

    private static void badParam(String param) {
        usage();
        System.out.println("");
        System.out.println("Unexpected parameter: '" + param + "'");
        System.exit(0);
    }

    private static void parseArgs(String[] args) {
        for (int i=0; i<args.length; i++) {
            if (args[i].equals("--help"))               { usage(); System.exit(0); }
            else if (args[i].equals("--moves"))         { i++; N = 3 * Integer.parseInt(args[i]); }
            else if (args[i].equals("--evaluations"))   { i++; sEvaluations = Integer.parseInt(args[i]); }
            else if (args[i].equals("--outdir"))        { i++; sOutDir = args[i]; }
            else                                        { badParam(args[i]); }
        }
    }

    public static void main(String[] args) {
        parseArgs(args);

        int[] ranges = new int[N];
        Arrays.fill(ranges, 2);

        // initialize our rubiks evaluator (including some initial moves)
        RubiksEvaluation ef = new RubiksEvaluation();
        String knownSolution = ef.scramble(N/3);

        Distribution odd = new DiscreteUniformDistribution(ranges);
        NeighborFunction nf = new DiscreteChangeOneNeighbor(ranges);
        MutationFunction mf = new DiscreteChangeOneMutation(ranges);
        Distribution df = new DiscreteDependencyTree(.1, ranges); 
        HillClimbingProblem hcp = new GenericHillClimbingProblem(ef, odd, nf);
        ProbabilisticOptimizationProblem pop = new GenericProbabilisticOptimizationProblem(ef, odd, df);

        CrossoverFunction[] cfs = { new UniformCrossOver(),
                                    new UniformCrossOver(3),
                                    new SingleCrossOver(),
                                    new SingleCrossOver(3),
                                    new TwoPointCrossOver(),
                                    new TwoPointCrossOver(3) };

        String[] cfnames = { "Uniform", "UniformStep3", "Single", "SingleStep3", "TwoPoint", "TwoPointStep3" };

        GeneticAlgorithmProblem[] gap = {   new GenericGeneticAlgorithmProblem(ef, odd, mf, cfs[0]),
                                            new GenericGeneticAlgorithmProblem(ef, odd, mf, cfs[1]),
                                            new GenericGeneticAlgorithmProblem(ef, odd, mf, cfs[2]),
                                            new GenericGeneticAlgorithmProblem(ef, odd, mf, cfs[3]),
                                            new GenericGeneticAlgorithmProblem(ef, odd, mf, cfs[4]),
                                            new GenericGeneticAlgorithmProblem(ef, odd, mf, cfs[5]) };
        
        /*
        RandomizedHillClimbing rhc = new RandomizedHillClimbing(hcp);      
        FixedIterationTrainer fit = new FixedIterationTrainer(rhc, 200);
        fit.train();
        System.out.println(ef.value(rhc.getOptimal()));
        */
        
        for (RubiksEvaluation.ValueType valueType : RubiksEvaluation.ValueType.values()) {
            ef.setValueType(valueType);
            Instance trueBest = null;
            // Instance trueBest = testEvaluation(ef, N);


            String name = "sa_"+valueType;
            PythonOut.startFile(name, sOutDir +"/"+ name +".py");
            SimulatedAnnealing sa = new SimulatedAnnealing(100, .98, hcp);
            UtilTrain.trainFixedEvaluations(sa, sEvaluations);
            printStatus(sa, ef, knownSolution, trueBest);
       
            for (int i=0; i<gap.length; i++)
            {
                name = "ga_"+valueType+cfnames[i]+"_oneChild";
                PythonOut.startFile(name, sOutDir +"/"+ name +".py");
                StandardGeneticAlgorithm ga = new StandardGeneticAlgorithm(1000, 500, true, 200, gap[i]);
                UtilTrain.trainFixedEvaluations(ga, sEvaluations);
                printStatus(ga, ef, knownSolution, trueBest);

                name = "ga_"+valueType+cfnames[i]+"_twoChildren";
                PythonOut.startFile(name, sOutDir +"/"+ name +".py");
                ga = new StandardGeneticAlgorithm(1000, 500, false, 200, gap[i]);
                UtilTrain.trainFixedEvaluations(ga, sEvaluations);
                printStatus(ga, ef, knownSolution, trueBest);
            }


            name = "mimic_"+valueType;
            PythonOut.startFile(name, sOutDir +"/"+ name +".py");
            MIMIC mimic = new MIMIC(1000, 500, pop);
            UtilTrain.trainFixedEvaluations(mimic, sEvaluations);
            printStatus(mimic, ef, knownSolution, trueBest);
        }
    }

    private static void printStatus(OptimizationAlgorithm oa, RubiksEvaluation ef, String knownSolution, Instance trueBest)
    {
        Instance optimalInstance = oa.getOptimal();
        double value = ef.value(optimalInstance);
        PythonOut.write("knownSolution", knownSolution);
        PythonOut.write("knownSolutionValue", ef.value(ef.knownSolution()));
        PythonOut.write("solves", ef.solvesPuzzle(optimalInstance) ? "True" : "False");
        PythonOut.write("optValue", value);
        PythonOut.write("moves", ef.movesToString(optimalInstance));
        if (trueBest != null) {
            PythonOut.write("trueBestValue", ef.value(trueBest));
            PythonOut.write("trueBestMoves", ef.movesToString(trueBest));
        }
    }
 
    /*
    public static void trainFixedEvaluations(OptimizationAlgorithm oa, int maxEvaluations) {
        int evaluations = 0;
        int iterations = 0;
        PythonOut.write(PythonOut.prefix+"['trainlabels'] = ['iterations','evaluations','bestvalue','bbestinstance','hbestinstance']\n");
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
                PythonOut.write("  [" + iterations+"," + evaluations+"," + bestValue+"," + binary+"],\n");
                // PythonOut.write("  [" + iterations+"," + evaluations+"," + bestValue+"," + binary+"," + hexString+"],\n");
            }
            iterations++;
        }
        PythonOut.write("]\n");
    }
    */

    // do bit math to increment vector
    private static Instance testEvaluation(RubiksEvaluation ef, int count) {
        Vector v = new DenseVector(count);
        Instance instance = new Instance(v);
        int max = 0;
        Instance maxInstance = null;
        Instance minSolver = null;
        Instance maxNonSolver = null;
        double minSolverValue = Double.MAX_VALUE;
        double maxNonSolverValue = -Double.MAX_VALUE;
        while (true) {
            int value = (int)ef.value(instance);
            if (ef.solvesPuzzle(instance)) {
                if (value < minSolverValue) {
                    minSolverValue = value;
                    minSolver = new Instance((Vector)v.copy());
                }
            }
            else {
                if (value > maxNonSolverValue) {
                    maxNonSolverValue = value;
                    maxNonSolver = new Instance((Vector)v.copy());
                }
            }
            if (minSolverValue <= maxNonSolverValue) {
                minSolverValue = ef.value(minSolver);
                maxNonSolverValue = ef.value(maxNonSolver);
            }

            if (maxInstance == null || value > max) {
                max = value;
                maxInstance = new Instance((Vector)v.copy());
            }
            if (!UtilTrain.incrementVector(v)) {
                break;
            }
        }
        return maxInstance;
    }
}
