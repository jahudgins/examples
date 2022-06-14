/**
 * Code modified from WekaDemo.java
 * @author Jonathan Hudgins
 * School: Georgia Tech
 * Class: CS7...
 */

import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.core.Attribute;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.OptionHandler;
import weka.core.Utils;
import weka.filters.Filter;

import java.io.FileReader;
import java.io.BufferedReader;
import java.lang.Math;
import java.util.Vector;


public class DecisionTree {
  /** the classifier used internally */
  protected Classifier m_Classifier = null;
  
  /** the filter to use */
  protected Filter m_Filter = null;

  /** the training file */
  protected String m_TrainingFile = null;

  /** the training instances */
  protected Instances m_Training = null;

  /** for evaluating the classifier */
  protected Evaluation m_Evaluation = null;

  /**
   * initializes the demo
   */
  public DecisionTree() {
    super();
  }

  /**
   * sets the classifier to use
   * @param name        the classname of the classifier
   * @param options     the options for the classifier
   */
  public void setClassifier(String name, String[] options) throws Exception {
    m_Classifier = Classifier.forName(name, options);
  }

  /**
   * sets the filter to use
   * @param name        the classname of the filter
   * @param options     the options for the filter
   */
  public void setFilter(String name, String[] options) throws Exception {
    m_Filter = (Filter) Class.forName(name).newInstance();
    if (m_Filter instanceof OptionHandler)
      ((OptionHandler) m_Filter).setOptions(options);
  }

  /**
   * sets the file to use for training
   */
  public void setTraining(String name) throws Exception {
    m_TrainingFile = name;
    m_Training     = new Instances(
                        new BufferedReader(new FileReader(m_TrainingFile)));
    m_Training.setClassIndex(m_Training.numAttributes() - 1);
  }

  // Begin jhudgins code

  static private float LOG_2 = (float)Math.log(2.0f);

  private class DecisionNode
  {
    public int numInstances;
    public Decision decision;
    public DecisionNode left;
    public DecisionNode right;
    public void printTree(String indent)
    {
      if (left!=null && right!=null)
      {
        double value = decision.instance.value(decision.attribute.index());
        System.out.println(indent + decision.attribute.name() + " < " + value + ":  count:" + left.numInstances);
        left.printTree(indent + "|   ");
        System.out.println(indent + decision.attribute.name() + " >= " + value + ":  count" + right.numInstances);
        right.printTree(indent + "|   ");
      }
      else if (left!=null || right!=null)
      {
        System.out.println("Error: left or right child exists without sibling");
      }
    }

  };

  private class Decision
  {
    public float gain;
    public Attribute attribute;
    public Instance instance;
  };

  private float log2(float value)
  {
    return (float)Math.log(value) / LOG_2;
  }

  // count how many instances for each classifier
  private void countClassifiers(int[] classifierBuckets, Instances instances)
  {
    for (int i=0; i<instances.numInstances(); i++)
    {
      classifierBuckets[(int)instances.instance(i).classValue()]++;
    }
  }

  // calculate entropy for attributes bucketed into classifiers
  private float calculateEntropy(int[] buckets, int numInstances)
  {
    float entropy = 0.0f;
    for (int i=0; i<buckets.length; i++)
    {
      if (buckets[i] > 0)
      {
        float proportion = (float)buckets[i] / numInstances;
        entropy += -proportion * log2(proportion);
      }
    }
    return entropy;
  }

  // calculate entropy for set of instances
  private float calculateEntropy(Instances instances)
  {
    int[] buckets = new int[instances.numClasses()];
    countClassifiers(buckets, instances);
    return calculateEntropy(buckets, instances.numInstances());
  }

  // calculate total entropy for decision that splits instances into rightBuckets and leftBuckets
  private float calculateTotalEntropy(int[] leftBuckets, int[] rightBuckets, int numInstances, int leftInstanceCount)
  {
    int rightInstanceCount = numInstances - leftInstanceCount;
    float leftEntropy = (float)leftInstanceCount / numInstances * calculateEntropy(leftBuckets, leftInstanceCount);
    float rightEntropy = (float)rightInstanceCount / numInstances * calculateEntropy(rightBuckets, rightInstanceCount);
    return leftEntropy + rightEntropy;
  }

  // calculate the gain for the best decision for the specified attribute
  // note: I don't handle missing values (I assume the data is complete by this point)
  private Decision bestDecisionForAttribute(Instances instances, int attributeIndex, float parentEntropy)
  {
    // we might be able to optimize by bucket sorting if the attribute is nominal
    // (weka might already optimize for this)
    instances.sort(attributeIndex);

    // keep track of attribute categories to the left and right of our decision
    // default initialization of 0
    int[] leftBuckets = new int[instances.numClasses()];
    int[] rightBuckets = new int[instances.numClasses()];
    countClassifiers(rightBuckets, instances);

    // check gain at each change in classification
    float maxGain = 0.0f;
    int maxGainIndex = 0;
    int lastClassification = (int)instances.instance(0).classValue();
    double lastValue = instances.instance(0).value(attributeIndex);
    rightBuckets[lastClassification]--;
    leftBuckets[lastClassification]++;
    for (int i=1; i<instances.numInstances(); i++)
    {
      int nextClassification = (int)instances.instance(i).classValue();
      double nextValue = instances.instance(i).value(attributeIndex);
      // if (nextClassification != lastClassification && nextValue > lastValue)
      if (nextValue > lastValue)
      {
        float gain = parentEntropy - calculateTotalEntropy(leftBuckets, rightBuckets, instances.numInstances(), i);
        if (gain > maxGain)
        {
          maxGain = gain;
          maxGainIndex = i;
        }
        // lastClassification = nextClassification;
        lastValue = nextValue;
      }
      rightBuckets[nextClassification]--;
      leftBuckets[nextClassification]++;
    }

    // perhaps for precision reasons we might be less than 0
    if (maxGain <= 0.0f)
    {
      return null;
    }

    Decision bestDecision = new Decision();
    bestDecision.gain = maxGain;
    bestDecision.attribute = instances.attribute(attributeIndex);
    bestDecision.instance = instances.instance(maxGainIndex);
    return bestDecision;
  }

  // determine best criteria to split on
  // then gather into left and right instances based on criteria  
  // maintain sorted lists for easier calculations of entropy
  private Decision splitInstances(Instances srcInstances, Instances leftInstances, Instances rightInstances)
  {
    // calculate current entropy
    float entropy = calculateEntropy(srcInstances);

    // calculate gain for each attribute and then pick the best
    Decision bestDecision = null;
    for (int i=0; i<srcInstances.numAttributes(); i++)
    {
      // don't try to split on the target classifier (of course that would be the best predictor!)
      if (i == srcInstances.classIndex())
      {
        continue;
      }

      Decision decision = bestDecisionForAttribute(srcInstances, i, entropy);
      if (bestDecision == null || (decision!=null && decision.gain > bestDecision.gain))
      {
        bestDecision = decision;
      }
    }

    if (bestDecision == null)
    {
      return null;
    }

    // add instances "less than" our decision instance to leftInstances and "greather or equal to" to rightInstances
    int bestAttributeIndex = bestDecision.attribute.index();
    double valueSplit = bestDecision.instance.value(bestAttributeIndex);
    for (int i=0; i<srcInstances.numInstances(); i++)
    {
      Instance instance = srcInstances.instance(i);
      if (instance.value(bestAttributeIndex) < valueSplit)
      {
        leftInstances.add(instance);
      }
      else
      {
        rightInstances.add(instance);
      }
    }

    return bestDecision;
  }


  // make a decision at this node, then recurse
  private DecisionNode buildRecursiveTree(Instances instances)
  {
    DecisionNode decisionNode = new DecisionNode();
    decisionNode.numInstances = instances.numInstances();

    /*
     * Should not be needed -- splitInstances should find case where no information gain
     * and return a null decision

    // base case when all instances fall into one classification
    if (allClassified(sortedInstances[0]))
    {
      return decisionNode;
    }
    */

    // allocate left, right
    // find best criteria and split
    Instances leftInstances = new Instances(instances, 0);
    Instances rightInstances = new Instances(instances, 0);
    decisionNode.decision = splitInstances(instances, leftInstances, rightInstances);
    if (decisionNode.decision == null)
    {
      return decisionNode;
    }

    // recurse on left and right
    decisionNode.left = buildRecursiveTree(leftInstances);
    decisionNode.right = buildRecursiveTree(rightInstances);

    return decisionNode;
  }

  /*
  public void buildDecisionTree(Instances instances)
  {
    DecisionNode decisionRoot = new DecisionNode();
    buildRecursiveTree(sortedInstances, decisionRoot);
  }
  */

  // End jhudgins code

  /**
   * runs 10fold CV over the training file
   */
  public void execute() throws Exception {
    // we want consistent results so run test before using random filter
    DecisionNode rootDecisionNode = buildRecursiveTree(m_Training);
    
    System.out.println("numAttributes:" + m_Training.numAttributes());
    System.out.println("numInstances:" + m_Training.numInstances());
    System.out.println("numClasses:" + m_Training.numClasses());

    rootDecisionNode.printTree("");
    // todo
    // error metrics / training / test set
    // pruning
    // print which attribute
    System.exit(1);


    // run filter
    m_Filter.setInputFormat(m_Training);
    Instances filtered = Filter.useFilter(m_Training, m_Filter);

    
    // train classifier on complete file for tree
    m_Classifier.buildClassifier(filtered);
    
    // 10fold CV with seed=1
    m_Evaluation = new Evaluation(filtered);
    m_Evaluation.crossValidateModel(
        m_Classifier, filtered, 10, m_Training.getRandomNumberGenerator(1));
  }

  /**
   * outputs some data about the classifier
   */
  public String toString() {
    StringBuffer        result;

    result = new StringBuffer();
    result.append("Weka - Demo\n===========\n\n");

    result.append("Classifier...: " 
        + m_Classifier.getClass().getName() + " " 
        + Utils.joinOptions(m_Classifier.getOptions()) + "\n");
    if (m_Filter instanceof OptionHandler)
      result.append("Filter.......: " 
          + m_Filter.getClass().getName() + " " 
          + Utils.joinOptions(((OptionHandler) m_Filter).getOptions()) + "\n");
    else
      result.append("Filter.......: "
          + m_Filter.getClass().getName() + "\n");
    result.append("Training file: " 
        + m_TrainingFile + "\n");
    result.append("\n");

    result.append(m_Classifier.toString() + "\n");
    result.append(m_Evaluation.toSummaryString() + "\n");
    try {
      result.append(m_Evaluation.toMatrixString() + "\n");
    }
    catch (Exception e) {
      e.printStackTrace();
    }
    try {
      result.append(m_Evaluation.toClassDetailsString() + "\n");
    }
    catch (Exception e) {
      e.printStackTrace();
    }
    
    return result.toString();
  }

  /**
   * returns the usage of the class
   */
  public static String usage() {
    return
        "\nusage:\n  " + DecisionTree.class.getName() 
        + "  CLASSIFIER <classname> [options] \n"
        + "  FILTER <classname> [options]\n"
        + "  DATASET <trainingfile>\n\n"
        + "e.g., \n"
        + "  java -classpath \".:weka.jar\" DecisionTree \n"
        + "    CLASSIFIER weka.classifiers.trees.J48 -U \n"
        + "    FILTER weka.filters.unsupervised.instance.Randomize \n"
        + "    DATASET iris.arff\n";
  }
  
  /**
   * runs the program, the command line looks like this:<br/>
   * DecisionTree CLASSIFIER classname [options] 
   *          FILTER classname [options] 
   *          DATASET filename 
   * <br/>
   * e.g., <br/>
   *   java -classpath ".:weka.jar" DecisionTree \<br/>
   *     CLASSIFIER weka.classifiers.trees.J48 -U \<br/>
   *     FILTER weka.filters.unsupervised.instance.Randomize \<br/>
   *     DATASET iris.arff<br/>
   */
  public static void main(String[] args) throws Exception {
    DecisionTree         demo;

    if (args.length < 6) {
      System.out.println(DecisionTree.usage());
      System.exit(1);
    }

    // parse command line
    String classifier = "";
    String filter = "";
    String dataset = "";
    Vector classifierOptions = new Vector();
    Vector filterOptions = new Vector();

    int i = 0;
    String current = "";
    boolean newPart = false;
    do {
      // determine part of command line
      if (args[i].equals("CLASSIFIER")) {
        current = args[i];
        i++;
        newPart = true;
      }
      else if (args[i].equals("FILTER")) {
        current = args[i];
        i++;
        newPart = true;
      }
      else if (args[i].equals("DATASET")) {
        current = args[i];
        i++;
        newPart = true;
      }

      if (current.equals("CLASSIFIER")) {
        if (newPart)
          classifier = args[i];
        else
          classifierOptions.add(args[i]);
      }
      else if (current.equals("FILTER")) {
        if (newPart)
          filter = args[i];
        else
          filterOptions.add(args[i]);
      }
      else if (current.equals("DATASET")) {
        if (newPart)
          dataset = args[i];
      }

      // next parameter
      i++;
      newPart = false;
    } 
    while (i < args.length);

    // everything provided?
    if ( classifier.equals("") || filter.equals("") || dataset.equals("") ) {
      System.out.println("Not all parameters provided!");
      System.out.println(DecisionTree.usage());
      System.exit(2);
    }

    // run
    demo = new DecisionTree();
    demo.setClassifier(
        classifier, 
        (String[]) classifierOptions.toArray(new String[classifierOptions.size()]));
    demo.setFilter(
        filter,
        (String[]) filterOptions.toArray(new String[filterOptions.size()]));
    demo.setTraining(dataset);
    demo.execute();
    System.out.println(demo.toString());
  }
}
