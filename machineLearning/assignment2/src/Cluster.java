
import shared.ConvergenceTrainer;
import shared.DataSet;
import shared.SumOfSquaresError;
import shared.filt.IndependentComponentAnalysis;
import shared.filt.LabelSplitFilter;
import shared.filt.LinearDiscriminantAnalysis;
import shared.filt.PrincipalComponentAnalysis;
import shared.filt.ProjectionFilter;
import shared.filt.RandomizedProjectionFilter;
import shared.reader.ArffDataSetReader;
import shared.reader.DataSetReader;
import util.PythonOut;
import func.EMClusterer;
import func.KMeansClusterer;
import func.nn.backprop.BackPropagationNetwork;
import func.nn.backprop.BackPropagationNetworkFactory;
import func.nn.backprop.BatchBackPropagationTrainer;
import func.nn.backprop.RPROPUpdateRule;

/**
 * Clustering and Attribute Transformation
 *
 * @author Jonathan Hudgins
 * @version 1.0
 */
public class Cluster {
    private static String sTestFile;
    private static String sTrainingFile;
    private static int sMaxAttributes = 20;
    private static int sAttributeStep = 2;
    private static int sNumHiddenNodes;
    private static String sOutputDir = ".";

    private static void usage() {
        System.out.println("Usage: Cluster [options]");
        System.out.println("--help                  print help");
        System.out.println("--testfile <file>       use ARFF <file> for the test data");
        System.out.println("--trainingfile <file>   use ARFF <file> for the training data");
        System.out.println("--maxattributes <n>     try transforms up to <n> attributes");
        System.out.println("--attributestep <n>     step <n> between attributes for filtereing");
        System.out.println("--outdir <dir>          directory for output");
        // System.out.println("--iterations <n>        run training for <n> interations");
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
            else if (args[i].equals("--maxattributes")) { i++; sMaxAttributes = Integer.parseInt(args[i]); }
            else if (args[i].equals("--attributestep")) { i++; sAttributeStep = Integer.parseInt(args[i]); }
            else if (args[i].equals("--outdir"))        { i++; sOutputDir = args[i]; }
            // else if (args[i].equals("--iterations"))    { i++; sTrainingIterations = Integer.parseInt(args[i]); }
            else                                        { badParam(args[i]); }
        }
    }

    public static void main(String[] args) {
        System.setProperty("line.separator", "\n");
        parseArgs(args);

        DataSet trainingDataset = LoadDataset(sTrainingFile);
        DataSet testDataset = LoadDataset(sTestFile);

        int numAttributes = trainingDataset.getDescription().getAttributeTypes().length;
        int numClasses = trainingDataset.getDescription().getLabelDescription().getDiscreteRange();
        sMaxAttributes = Math.min(sMaxAttributes, numAttributes - 1);
        sNumHiddenNodes = (sMaxAttributes + numClasses) / 2;

        String name = "Baseline";
        //PythonOut.startFile(name, sOutputDir + "/" + name + ".py");
        //AnalyzeClustering("Baseline", trainingDataset, testDataset, false);
        //AnalyzeNeuralNetwork("Baseline", trainingDataset, testDataset);

        for (int i=8; i<=sMaxAttributes; i += sAttributeStep) {
            PrincipalComponentAnalysis pca = new PrincipalComponentAnalysis(trainingDataset, i);
            AnalyzeTransform(pca, i, "PCA_"+i, trainingDataset, testDataset);
            PythonOut.write("PCAEigenValuesAttributes", pca.getEigenValues());

            IndependentComponentAnalysis ica = new IndependentComponentAnalysis(trainingDataset, i);
            AnalyzeTransform(ica , i, "ICA_"+i, trainingDataset, testDataset);

            for (int j=0; j<1; j++) {
                RandomizedProjectionFilter rpf = new RandomizedProjectionFilter(i, numAttributes);
                AnalyzeTransform(rpf, i, "RandomizedProjectionFilter_"+i+"_"+j, trainingDataset, testDataset);
                // PythonOut.write("RandomizedProjectionFilter"+i+"_"+j, rpf.getReconstruction(trainingDataset));
            }
        }

        LinearDiscriminantAnalysis lda = new LinearDiscriminantAnalysis(trainingDataset);
        AnalyzeTransform(lda, numClasses, "LinearDiscriminantAnalysis", trainingDataset, testDataset);
        // PythonOut.write("LinearDiscriminantAnalysis"+i, lda.getMeasure(trainingDataset));
    }

    private static void AnalyzeTransform(ProjectionFilter filter, int numFilteredAttributes, String name,
                                    DataSet trainingDataset, DataSet testDataset)
    {
        PythonOut.startFile(name, sOutputDir + "/" + name + ".py");

        PythonOut.write("preKurtosis", trainingDataset.calculateKurtosis());

        DataSet trainingFiltered = trainingDataset.copy();
        DataSet testFiltered = testDataset.copy();
        filter.filter(trainingFiltered);
        filter.filter(testFiltered);
        PythonOut.write("projection", filter.getProjection());
        PythonOut.write("postKurtosis", trainingFiltered.calculateKurtosis());

        if (numFilteredAttributes == 2) {
            PythonOut.write("data2d", trainingFiltered);
        }

        DataSet[] clusteredSets = AnalyzeClustering("Filtered", trainingFiltered, testFiltered, true);

        if (numFilteredAttributes == 2) {
            PythonOut.write("data2dClustered", clusteredSets[0]);
        }

        AnalyzeNeuralNetwork("Filtered", trainingFiltered, testFiltered);

        AnalyzeNeuralNetwork("FilteredWithCluster", clusteredSets[0], clusteredSets[1]);

    }

    private static void AnalyzeNeuralNetwork(String name, DataSet trainingDataset, DataSet testDataset)
    {
        int numAttributes = trainingDataset.getDescription().getAttributeTypes().length;
        int numClasses = trainingDataset.getDescription().getLabelDescription().getDiscreteRange();
        BackPropagationNetworkFactory factory = new BackPropagationNetworkFactory();
        BackPropagationNetwork network = factory.createClassificationNetwork(
                                            new int[] { numAttributes, sNumHiddenNodes, numClasses });
        ConvergenceTrainer trainer = new ConvergenceTrainer(
                                        new BatchBackPropagationTrainer(
                                            trainingDataset, network, new SumOfSquaresError(), new RPROPUpdateRule()),
                                        1E-5, 2000);
        double start = System.nanoTime();
        trainer.train();
        double end = System.nanoTime();
        double trainingTime = (end - start) / Math.pow(10,9);
        double numTrainingInstances = trainingDataset.getInstances().length;
        double numTestInstances = testDataset.getInstances().length;
        double trainingCorrect = network.countCorrect(trainingDataset.getInstances()) / numTrainingInstances;
        double testCorrect = network.countCorrect(testDataset.getInstances()) / numTestInstances;
        PythonOut.write(name+"NeuralNetworkTrainCorrect", trainingCorrect);
        PythonOut.write(name+"NeuralNetworkTestCorrect", testCorrect);
        PythonOut.write(name+"NeuralNetworkTime", trainingTime);
        PythonOut.write(name+"NeuralNetworkIterations", trainer.getIterations());
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

    private static void AnalyzeClustering(String name, DataSet dataset, boolean addAttribute)
    {
        // get some useful information from the dataset
        int numClasses = dataset.getDescription().getLabelDescription().getDiscreteRange();

        KMeansClusterer kmeansClusterer = new KMeansClusterer(numClasses);
        kmeansClusterer.estimate(dataset);
        kmeansClusterer.toPython("kmeans");
        PythonOut.write("kmeansLabelCompare", kmeansClusterer.labelComparisonMatrix(dataset));

        EMClusterer emClusterer = new EMClusterer(numClasses, 1E-5, 100);
        emClusterer.estimate(dataset);
        emClusterer.getMixture().pythonOut("emCluster_end");
        PythonOut.write("emIterations", emClusterer.getIterations());
        PythonOut.write("emElapsedTime", emClusterer.getElapsedTime());
        PythonOut.write("emLabelCompare", emClusterer.labelComparisonMatrix(dataset));

        if (addAttribute) {
            // need to add emClusterer attribute first (otherwise vector math mismatches dimensions)
            emClusterer.addClusterAsAttribute(dataset);
            kmeansClusterer.addClusterAsAttribute(dataset);
        }
    }

    private static DataSet[] AnalyzeClustering(String name, DataSet trainingSet, DataSet testSet, boolean addAttribute)
    {
        // combine datasets
        DataSet combined = trainingSet.copy();
        combined.appendCopy(testSet);
        
        AnalyzeClustering(name, combined, addAttribute);

        DataSet[] returnSets = new DataSet[2];
        returnSets[0] = combined.splitNew(0, trainingSet.size());
        returnSets[1] = combined.splitNew(trainingSet.size(), testSet.size());
        return returnSets;
    }

}
