
import java.text.DecimalFormat;

import opt.OptPolicy;
import opt.OptimizationAlgorithm;
import opt.RandomRestartHillClimbing;
import opt.SimulatedAnnealing;
import opt.example.NeuralNetworkOptimizationProblem;
import opt.ga.StandardGeneticAlgorithm;
import shared.ConvergenceTrainer;
import shared.DataSet;
import shared.ErrorMeasure;
import shared.Instance;
import shared.SumOfSquaresError;
import shared.filt.LabelSplitFilter;
import shared.reader.ArffDataSetReader;
import shared.reader.DataSetReader;
import util.PythonOut;
import util.linalg.DenseVector;
import util.linalg.Vector;
import func.nn.backprop.BackPropagationNetwork;
import func.nn.backprop.BackPropagationNetworkFactory;
import func.nn.backprop.BatchBackPropagationTrainer;
import func.nn.backprop.RPROPUpdateRule;

/**
 * Implementation of randomized hill climbing, simulated annealing, and genetic algorithm to
 * find optimal weights to a neural network that is classifying spoken letters (isolet)
 *
 * Modified from ABAGAIL distribution
 *      ABAGAIL/src/opt/test/AbaloneTest.java
 * original author: Hannah Lau
 *
 * @author Jonathan Hudgins
 * @version 1.0
 */
public class TrainNeuralNet {
    private static int sTrainingEvaluations = 100;
    private static BackPropagationNetworkFactory factory = new BackPropagationNetworkFactory();
    
    private static ErrorMeasure measure = new SumOfSquaresError();

    private static BackPropagationNetwork networks[] = new BackPropagationNetwork[8];
    private static NeuralNetworkOptimizationProblem[] nnop = new NeuralNetworkOptimizationProblem[8];

    private static OptimizationAlgorithm[] oa = new OptimizationAlgorithm[5];
 
    private static DecimalFormat df = new DecimalFormat("0.000");

    private static String sTestFile;
    private static String sTrainingFile;
    private static String sOutDir = ".";
    private static Double sBaselineError = 1e-5;

    private static DataSet sTrainingDataset;
    private static DataSet sTestDataset;

    private static void usage() {
        System.out.println("Usage: TrainNeuralNet [options]");
        System.out.println("--help                  print help");
        System.out.println("--testfile <file>       use ARFF <file> for the test data");
        System.out.println("--trainingfile <file>   use ARFF <file> for the training data");
        System.out.println("--evaluations <n>       run optimization algorithms for <n> evaluations");
        System.out.println("--outdir <dir>          write output to <dir> directory");
        System.out.println("--baseline <error>      stop baseline training at <error>");
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
            else if (args[i].equals("--testfile"))      { i++; sTestFile = args[i]; }
            else if (args[i].equals("--trainingfile"))  { i++; sTrainingFile = args[i]; }
            else if (args[i].equals("--evaluations"))   { i++; sTrainingEvaluations = Integer.parseInt(args[i]); }
            else if (args[i].equals("--outdir"))        { i++; sOutDir = args[i]; }
            else if (args[i].equals("--baseline"))      { i++; sBaselineError = Double.parseDouble(args[i]); }
            else                                        { badParam(args[i]); }
        }
    }

    private static void reportBaseline() {
        PythonOut.startFile("Baseline", sOutDir + "/Baseline.py");
        int numAttributes = sTrainingDataset.getDescription().getAttributeTypes().length;
        int numClasses = sTrainingDataset.getDescription().getLabelDescription().getDiscreteRange();
        int hiddenLayer = 10; // high hidden layers makes this strategy intractible (numAttributes + numClasses) / 2;
        BackPropagationNetworkFactory factory = new BackPropagationNetworkFactory();
        BackPropagationNetwork network = factory.createClassificationNetwork(
                                            new int[] { numAttributes, hiddenLayer, numClasses });
        ConvergenceTrainer trainer = new ConvergenceTrainer(
                                        new BatchBackPropagationTrainer(
                                            sTrainingDataset, network, new SumOfSquaresError(), new RPROPUpdateRule()),
                                        sBaselineError, 2000);

        double start = System.nanoTime();
        trainer.train();
        double end = System.nanoTime();
        double trainingTime = (end - start) / Math.pow(10,9);
        double numTrainingInstances = sTrainingDataset.getInstances().length;
        double numTestInstances = sTestDataset.getInstances().length;
        double trainingCorrect = network.countCorrect(sTrainingDataset.getInstances()) / numTrainingInstances;
        double testCorrect = network.countCorrect(sTestDataset.getInstances()) / numTestInstances;
        PythonOut.write("trainCorrect", trainingCorrect);
        PythonOut.write("testCorrect", testCorrect);
        PythonOut.write("time", trainingTime);
        PythonOut.write("iterations", trainer.getIterations());
    }

    public static void main(String[] args) {
        parseArgs(args);
        sTrainingDataset = LoadDataset(sTrainingFile);
        sTestDataset = LoadDataset(sTestFile);

        reportBaseline();

        // get some useful information from the dataset
        int numAttributes = sTrainingDataset.getDescription().getAttributeTypes().length;
        int numClasses = sTrainingDataset.getDescription().getLabelDescription().getDiscreteRange();

        int hiddenLayer = 10; // high hidden layers makes this strategy intractible (numAttributes + numClasses) / 2;

        for(int i = 0; i < oa.length; i++) {
            networks[i] = factory.createClassificationNetwork(new int[] {numAttributes, hiddenLayer, numClasses});
            nnop[i] = new NeuralNetworkOptimizationProblem(sTrainingDataset, networks[i], measure);
        }

        // to help with convergence, only count improvements that are better than 10%
        double improvementThreshhold = 1.1;
        double incrementDefault = 0.5;
        double restartChance = 0.001;
        //                                  network,   dimension choice,                            increment choice,                     restart choice
        oa[0] = new RandomRestartHillClimbing(nnop[0], OptPolicy.Random,     1.00, OptPolicy.Random,   incrementDefault, OptPolicy.Random,   restartChance);
        oa[1] = new RandomRestartHillClimbing(nnop[1], OptPolicy.RoundRobin, 1.02, OptPolicy.Constant, incrementDefault, OptPolicy.Random, restartChance);
        oa[2] = new RandomRestartHillClimbing(nnop[2], OptPolicy.Converge,   1.02, OptPolicy.Converge, incrementDefault, OptPolicy.Converge, 0);
        String[] algorithmNames = { 
            "HillClimbRandomAll",
            "HillClimbRoundRobinDim",
            "HillClimbConverge",
            "SimulatedAnnealing",
            "GeneticAlgorithm"
        };


        oa[3] = new SimulatedAnnealing(1E11, .95, nnop[3]);
        oa[4] = new StandardGeneticAlgorithm(200, 100, 10, nnop[4]);

        int numWeights = networks[0].getLinks().size();

        // train and report each algorithm
        // for(int i = 0; i < oa.length; i++)
        int i = 4;
        {
            PythonOut.startFile(algorithmNames[i], sOutDir + "/" + algorithmNames[i] + ".py");

            // allocate stats outside loop to keep it out of the timing
            Stats[] stats = new Stats[Math.min(500, sTrainingEvaluations)];
            for (int j=0; j<stats.length; j++) {
                stats[j] = new Stats();
                stats[j].weights = new DenseVector(numWeights);
            }

            // train (time it too!)
            double start = System.nanoTime(), end, trainingTime;
            train(oa[i], networks[i], stats);
            end = System.nanoTime();
            trainingTime = (end - start) / Math.pow(10,9);

            // report
            report(stats, oa[i], networks[i], trainingTime);
            if (i <= 2) {
                randomRestartReport(oa[i]);
            }
        }
    }

    private static void randomRestartReport(OptimizationAlgorithm oa)
    {
        RandomRestartHillClimbing rrhc = (RandomRestartHillClimbing)oa;
        PythonOut.write("restarts", rrhc.getRestarts());
        PythonOut.write("dimensionChanges", rrhc.getDimensionChanges());
    }

    private static void report(Stats[] stats, OptimizationAlgorithm oa, BackPropagationNetwork network,
                                double trainingTime) {
        PythonOut.write("trainingTime",  trainingTime);
        PythonOut.write(PythonOut.prefix+"['trainlabels'] = ['iterations','evaluations','fitness','bestfitness','trainCorrect','testCorrect']\n");

        PythonOut.write(PythonOut.prefix+"['train'] = [\n");
        for (int i=0; i<stats.length; i++) {
            if (stats[i].weights == null) {
                break;
            }

            // calculate training test correct
            int trainingCorrect = 0;
            int testCorrect = 0;
            network.setWeights(stats[i].weights);
            trainingCorrect = network.countCorrect(sTrainingDataset.getInstances());
            testCorrect = network.countCorrect(sTestDataset.getInstances());
            double trainingProportion = (double)trainingCorrect / sTrainingDataset.getInstances().length;
            double testProportion = (double)testCorrect / sTestDataset.getInstances().length;

            PythonOut.write("  [");
            PythonOut.write(stats[i].iterations);
            PythonOut.write(",");
            PythonOut.write(stats[i].evaluations);
            PythonOut.write(",");
            PythonOut.write(stats[i].fitness);
            PythonOut.write(",");
            PythonOut.write(stats[i].bestfitness);
            PythonOut.write(",");
            PythonOut.write(trainingProportion);
            PythonOut.write(",");
            PythonOut.write(testProportion);
            PythonOut.write(",");
            PythonOut.write("],\n");
        }
        PythonOut.write("]\n");
    }


    // Load data set from Arff
    private static DataSet LoadDataset(String filename) {
        DataSetReader reader = new ArffDataSetReader(filename);
        try {
            DataSet dataSet = reader.read();
            LabelSplitFilter labelSplitFilter = new LabelSplitFilter();
            labelSplitFilter.filter(dataSet);
            return dataSet;
        }
        catch(Exception e) {
            System.out.println("\nFailed to load file, '" + filename + "', due to exception:");
            System.out.println("    " + e);
            System.exit(0);
            return null;
        }
    }

    static class Stats {
        public int iterations;
        public int evaluations;
        public double fitness;
        public double bestfitness;
        public Vector weights;
    }

    private static void train(OptimizationAlgorithm oa, BackPropagationNetwork network, Stats[] stats) {

        // train up to specified iterations
        Instance[] trainingInstances = sTrainingDataset.getInstances();
        int iterations = 0;
        int evaluations = 0;
        int statsIndex = 0;
        int statsStep = sTrainingEvaluations / stats.length;
        while (evaluations < sTrainingEvaluations) {
            oa.train();
            evaluations = oa.getEvaluations();
            iterations++;

            if (evaluations >= (statsIndex + 1) * statsStep) {

                // every countPerStat iterations, save the stats for later reporting
                // copy values -- make sure no memory allocations to reduce
                // time overhead
                stats[statsIndex].iterations = iterations;
                stats[statsIndex].evaluations = evaluations;
                stats[statsIndex].fitness = oa.getOptimalValue();
                stats[statsIndex].bestfitness = oa.getBestOptimalValue();
                Instance optimalInstance = oa.getOptimal();
                for (int i=0; i<optimalInstance.size(); i++) {
                    stats[statsIndex].weights.set(i, optimalInstance.getContinuous(i));
                }
                statsIndex++;
            }
        }
        // signify end of stats
        if (statsIndex < stats.length) {
            stats[statsIndex].weights = null;
        }
    }
}
