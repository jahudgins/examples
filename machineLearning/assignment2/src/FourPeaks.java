import java.util.Arrays;

import opt.DiscreteChangeOneNeighbor;
import opt.GenericHillClimbingProblem;
import opt.HillClimbingProblem;
import opt.NeighborFunction;
import opt.SimulatedAnnealing;
import opt.ga.CrossoverFunction;
import opt.ga.DiscreteChangeOneMutation;
import opt.ga.GenericGeneticAlgorithmProblem;
import opt.ga.GeneticAlgorithmProblem;
import opt.ga.MutationFunction;
import opt.ga.StandardGeneticAlgorithm;
import opt.ga.UniformCrossOver;
import opt.prob.GenericProbabilisticOptimizationProblem;
import opt.prob.MIMIC;
import opt.prob.ProbabilisticOptimizationProblem;
import util.PythonOut;
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

public class FourPeaks {
    /** The n value */
    private static int N = 15;
    private static int sEvaluations = -1;
    private static String sOutDir = ".";
    private static int sPopulation = 200;
    private static boolean sPopSpecified = false;
    private static double sKeepratio = .5;
    private static double sTemperature = 10;
    private static boolean sTempOnly = false;

    private static void usage() {
        System.out.println("Usage: FourPeaks [options]");
        System.out.println("--help              print help");
        System.out.println("--length <n>        <n> length of bit strings");
        System.out.println("--evaluations <n>   run training for <n> evaluations");
        System.out.println("--population <n>    <n> population for GA and MIMIC");
        System.out.println("--keepratio <r>     ratio <r> of population to keep");
        System.out.println("--temponly <t>      temperature <t> for SA only");
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
            else if (args[i].equals("--length"))        { i++; N = Integer.parseInt(args[i]); }
            else if (args[i].equals("--evaluations"))   { i++; sEvaluations = Integer.parseInt(args[i]); }
            else if (args[i].equals("--outdir"))        { i++; sOutDir = args[i]; }
            else if (args[i].equals("--population"))    { i++; sPopulation = Integer.parseInt(args[i]); sPopSpecified = true; }
            else if (args[i].equals("--keepratio"))     { i++; sKeepratio = Double.parseDouble(args[i]); }
            else if (args[i].equals("--temponly"))      { i++; sTemperature = Double.parseDouble(args[i]); sTempOnly = true; }
            else                                        { badParam(args[i]); }
        }
    }

    public static void main(String[] args) {
        parseArgs(args);

        int[] ranges = new int[N];
        Arrays.fill(ranges, 2);

        PythonOut.startFile("distribution", sOutDir + "/" + "distribution.py");
        FourPeaksEvaluation ef = new FourPeaksEvaluation(N, N/5);
        int max = ef.max(N);
        // don't try doing this for more than 512, we will get stuck here real quick
        if (N < 10) {
            int[] dist = UtilTrain.distribution(ef, N);
            PythonOut.write("values", dist);
        }
        PythonOut.write("stringlength", N);
        PythonOut.write("max", max);

        /*
        if (N <= 30) {
            int foundmax = UtilTrain.findmax(ef, N);
            PythonOut.write("foundmax", foundmax);
        }
        */


        Distribution odd = new DiscreteUniformDistribution(ranges);
        NeighborFunction nf = new DiscreteChangeOneNeighbor(ranges);
        MutationFunction mf = new DiscreteChangeOneMutation(ranges);
        CrossoverFunction cf = new UniformCrossOver();
        Distribution df = new DiscreteDependencyTree(.1, ranges); 
        HillClimbingProblem hcp = new GenericHillClimbingProblem(ef, odd, nf);
        GeneticAlgorithmProblem gap = new GenericGeneticAlgorithmProblem(ef, odd, mf, cf);
        ProbabilisticOptimizationProblem pop = new GenericProbabilisticOptimizationProblem(ef, odd, df);
        
        int mimicpop = 50;
        int mimickeep = 5;
        int gapop = 1000;
        int gakeep = 750;

        if (sPopSpecified) {
            int keep = (int)(sPopulation * sKeepratio);
            mimicpop = sPopulation;
            mimickeep = keep;
            gapop = sPopulation;
            gakeep = keep;
        }

        int mutate = (int)(0.05 * gapop);
        double cooling;
        if (sEvaluations == -1) {
            cooling = Math.exp(Math.log(.1)/Math.max(1000, Math.pow(2, N/4)));
        } else {
            cooling = Math.exp(Math.log(.1)/sEvaluations);
        }

        PythonOut.write("sa-temp", sTemperature);
        PythonOut.write("sa-cooling", cooling);
        PythonOut.write("ga-pop", gapop);
        PythonOut.write("ga-keep", gakeep);
        PythonOut.write("ga-mutate", mutate);
        PythonOut.write("mimic-pop", mimicpop);
        PythonOut.write("mimic-keep", mimickeep);

        int printStep = (int)Math.min(Math.pow(2, N)/1000, 1000);

        String name = sTempOnly ? "sa" + (int)sTemperature : "SimulatedAnnealing";
        PythonOut.startFile(name, sOutDir + "/" + name + ".py");
        SimulatedAnnealing sa = new SimulatedAnnealing(sTemperature, cooling, hcp);
        UtilTrain.trainUntilMax(sa, max, sEvaluations, printStep);
        
        if (!sTempOnly) {
            PythonOut.startFile("GeneticAlgorithm", sOutDir + "/GeneticAlgorithm.py");
            StandardGeneticAlgorithm ga = new StandardGeneticAlgorithm(gapop, gapop-gakeep, mutate, gap);
            UtilTrain.trainUntilMax(ga, max, sEvaluations, printStep);

            PythonOut.startFile("MIMIC", sOutDir + "/MIMIC.py");
            MIMIC mimic = new MIMIC(mimicpop, mimickeep, pop);
            UtilTrain.trainUntilMax(mimic, max, sEvaluations, printStep);
        }
    }
}
