import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
import importlib
import sys

from matplotlib.font_manager import FontProperties


def plotNNdata(data, typeKeyPrefixes, typeKeySuffix, typePrefixNames, caption):
    global args

    fig = plt.figure()
    subplot = fig.add_subplot(111)

    plots = []
    attributes = range(2, args.maxattributes+1, args.attributestep)
    for typeKeyPrefix in typeKeyPrefixes:
        typeKey = typeKeyPrefix + typeKeySuffix
        pca = []
        ica = []
        rpf = []
        for i in attributes:
            pca.append(data['PCA_{0}'.format(i)][typeKey])
            ica.append(data['ICA_{0}'.format(i)][typeKey])
            rpf_value = 0.0
            for j in range(5):
                rpf_value += data['RandomizedProjectionFilter_{0}_{1}'.format(i, j)][typeKey]
            rpf.append(rpf_value / 5)

        plots.append(subplot.plot(attributes, pca)[0])
        plots.append(subplot.plot(attributes, ica)[0])
        plots.append(subplot.plot(attributes, rpf)[0])

    labels = []
    for typePrefixName in typePrefixNames:
        labels.append('PCA {0}'.format(typePrefixName))
        labels.append('ICA {0}'.format(typePrefixName))
        labels.append('RPF {0}'.format(typePrefixName))

    font = FontProperties()
    font.set_size('small')
    plt.legend(plots, labels, loc='upper center', fancybox = True, ncol=2, bbox_to_anchor=(.5, 1.1), prop=font)
    # plt.legend(plots[0:3], labels[0:3], loc=3, prop=font)
    # plt.legend(plots[3:6], labels[3:6], loc=4, prop=font)
    # plt.legend(plots, labels, loc=2, bbox_to_anchor=(1.05, 1))
    # plt.legend(plots, labels, bbox_to_anchor=(0, 0, 1, 1), bbox_transform=gcf().transFigure)
    plt.xlabel('Number of Attributes after Filtered')
    plt.ylabel(caption)
    plt.xlim(1, args.maxattributes + 1)
    plt.savefig(args.plots + "/" + caption + ".png")

def plot2dclusters(data, typeName):
    points = data['data2dClustered']
    x = []
    y = []
    label = []
    emCluster = []
    kCluster = []

    emMin = points[0][2]
    emMax = points[0][2]
    kMin = points[0][4]
    kMax = points[0][4]

    count = 0
    for point in points:
        x.append(point[0])
        y.append(point[1])
        label.append(point[-1])
        if point[3] < .90:
            count += 1
            emCluster.append('black')
        else:
            emCluster.append(point[2])
        emMin = min(emMin, point[2])
        emMax = max(emMax, point[2])
        kCluster.append(point[4])
        kMin = min(kMin, point[4])
        kMax = max(kMax, point[4])

    print count

    color = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow']
    emColor = []
    for em in emCluster:
        if em == 'black':
            emColor.append(em)
        else:
            colorIndex = int((em - emMin) * (emMax - emMin)) % len(color)
            emColor.append(color[colorIndex])

    kCluster = map(lambda x: int((x - kMin) * (kMax - kMin)), kCluster)
    plotScatter(typeName + "Label", x, y, label)
    plotScatter(typeName + "EMcluster", x, y, emColor)
    plotScatter(typeName + "KmeansCluster", x, y, kCluster)

def plotScatter(typeName, x, y, color):
    fig = plt.figure()
    subplot = fig.add_subplot(111)
    plt.scatter(x, y, c=color, alpha=0.5)
    plt.xlabel(typeName)
    plt.savefig(args.plots + "/" + typeName + ".png")

def printCompareTable(matrix, name):
    print "{0} Comparison Matrix".format(name)
    print "labels,",
    for i in range(len(matrix[0])):
        print "{0},".format(i+1),
    print

    total = 0
    for v in matrix:
        total += sum(v)

    for i in range(len(matrix)):
        print "{0},".format(i+1),
        for j in range(len(matrix[i])):
            print "{0:.4f},".format(matrix[i][j]/total),
        print

    print

def printClusters(kmeans):
    print "cluster,instances,mean to centroid,min to centroid,max to centroid,std dev to centroid,mean to next centroid,normalized volume"
    count = 0
    for cluster in kmeans['clusters']:
        print "{0},".format(count+1),
        print "{0},".format(int(cluster['instances'])),
        print "{0},".format(cluster['meanToCentroid']),
        print "{0},".format(cluster['minToCentroid']),
        print "{0},".format(cluster['maxToCentroid']),
        print "{0},".format(cluster['stdDevToCentroid']),
        print "{0},".format(cluster['meanToNextCentroid']),
        print "{0},".format(cluster['normalizedVolume']),
        print
        count += 1
    

def printEM(filedata):
    print "EM distribution".format(filedata['emCluster_endDistribution'])

def printKurtosis(data):
    global args
    print "kurtosis,",
    for i in range(2, args.maxattributes+1, args.attributestep):
        print "{0},".format(i),
    print
    for i in range(2, args.maxattributes+1, args.attributestep):
        name = "ICA_{0}".format(i)
        print "{0},".format(i),
        for k in data[name]['postKurtosis']:
            print "{0},".format(k),
        print
    print


def analyzeBaseline(data):
    printCompareTable(data['Baseline']['kmeansLabelCompare'], 'KMeans Baseline')
    printCompareTable(data['Baseline']['emLabelCompare'], 'EM Baseline')
    printClusters(data['Baseline']['kmeans'])
    printEM(data['Baseline'])

def importFile(data, name):
    module = importlib.import_module(name)
    data[name] = eval("module.{0}".format(name))

parser = argparse.ArgumentParser(description='Plot graphs based on data from clustering experiments.')
parser.add_argument('--maxattributes', type=int, required=True, help='maximum attributes used')
parser.add_argument('--attributestep', type=int, default=2, help='step between attributes')
parser.add_argument('--directory', required=True, help='directory to read files output by experiments')
parser.add_argument('--plots', required=True, help='directory to write plots')
args = parser.parse_args()

sys.path.append(args.directory)

data = {}
importFile(data, "Baseline")

importFile(data, "LinearDiscriminantAnalysis")
#printCompareTable(data['LinearDiscriminantAnalysis']['kmeansLabelCompare'], 'KMeans LDA')
#sys.exit(1)

for i in range(2, args.maxattributes+1, 2):
    importFile(data, "PCA_{0}".format(i))
    importFile(data, "ICA_{0}".format(i))
    importFile(data, "RandomizedProjectionFilter_{0}_{1}".format(i, 0))

print "Filtered"
print 'TrainCorrect',
print 'TestCorrect',
print 'Time',
print 'Iterations',
print

for key, value in data.items():
    if not value.has_key('FilteredWithClusterNeuralNetworkTrainCorrect'):
        continue
    print key + ",",
    print value['FilteredNeuralNetworkTrainCorrect'],
    print value['FilteredNeuralNetworkTestCorrect'],
    print value['FilteredNeuralNetworkTime'],
    print value['FilteredNeuralNetworkIterations'],
    print

print
print


print "W/ Cluster Attribute"
print 'TrainCorrect',
print 'TestCorrect',
print 'Time',
print 'Iterations',
print

for key, value in data.items():
    if not value.has_key('FilteredWithClusterNeuralNetworkTrainCorrect'):
        continue
    print key + ",",
    print value['FilteredWithClusterNeuralNetworkTrainCorrect'],
    print value['FilteredWithClusterNeuralNetworkTestCorrect'],
    print value['FilteredWithClusterNeuralNetworkTime'],
    print value['FilteredWithClusterNeuralNetworkIterations'],
    print


sys.exit(1)

printKurtosis(data)
analyzeBaseline(data)

filteredTags = ['Filtered', 'FilteredWithCluster']
filteredNames = ['Filtered', 'Filtered w/ Cluster']

plotNNdata(data, filteredTags, 'NeuralNetworkTime', filteredNames, 'Time')
plotNNdata(data, filteredTags, 'NeuralNetworkTrainCorrect', filteredNames, 'TrainCorrect')
plotNNdata(data, filteredTags, 'NeuralNetworkTestCorrect', filteredNames, 'TestCorrect')
plotNNdata(data, filteredTags, 'NeuralNetworkIterations', filteredNames, 'Iterations')

plot2dclusters(data['ICA_2'], "ICA")
plot2dclusters(data['PCA_2'], "PCA")
plot2dclusters(data['RandomizedProjectionFilter_2_0'], "RPF0")
plot2dclusters(data['RandomizedProjectionFilter_2_1'], "RPF1")
plot2dclusters(data['RandomizedProjectionFilter_2_2'], "RPF2")
