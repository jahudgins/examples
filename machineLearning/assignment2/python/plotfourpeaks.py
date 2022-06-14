import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
import importlib
import sys
import math
import pdb

from matplotlib.font_manager import FontProperties


def plotDistribution(data):
    importFile(data, 'distribution')

    if not data['distribution'].has_key('values'):
        return

    fig = plt.figure()
    subplot = fig.add_subplot(111)
    values = data['distribution']['values']
    x = range(len(values)-1, 0-1, -1)

    subplot.bar(x, values, color='black')

    plt.savefig(args.plots + "/distribution.png")


def plotTraining(data, subplot, tags, name, plots, labels):
    xIndex = data[name]['trainlabels'].index(tags[0])
    yIndex = data[name]['trainlabels'].index(tags[1])
    values = data[name]['train']

    x = []
    y = []
    for value in values:
        x.append(value[xIndex])
        y.append(value[yIndex])


def importFile(data, name):
    module = importlib.import_module(name)
    data[name] = eval("module.{0}".format(name))

parser = argparse.ArgumentParser(description='Plot graphs based on data from clustering experiments.')
parser.add_argument('--directory', required=True, help='directory to read files output by experiments')
parser.add_argument('--plots', required=True, help='directory to write plots')
args = parser.parse_args()

sys.path.append(args.directory)

data = {}
plotDistribution(data)

"""
data = {}
data['SimulatedAnnealing'] = {}
data['GeneticAlgorithm'] = {}
data['MIMIC'] = {}

data['SimulatedAnnealing']['10.1'] = 209
data['GeneticAlgorithm']['10.1'] = 1250
data['MIMIC']['10.1'] = 450
data['SimulatedAnnealing']['10.2'] = 93
data['GeneticAlgorithm']['10.2'] = 1250
data['MIMIC']['10.2'] = 600
data['SimulatedAnnealing']['15.1'] = 872
data['GeneticAlgorithm']['15.1'] = 1500
data['MIMIC']['15.1'] = 200
data['SimulatedAnnealing']['15.2'] = 521
data['GeneticAlgorithm']['15.2'] = 1750
data['MIMIC']['15.2'] = 131300
data['SimulatedAnnealing']['20.1'] = 788
data['GeneticAlgorithm']['20.1'] = 2750
data['MIMIC']['20.1'] = 7000
data['SimulatedAnnealing']['20.2'] = 752
data['GeneticAlgorithm']['20.2'] = 3250
data['MIMIC']['20.2'] = 2650
data['SimulatedAnnealing']['25.1'] = 1416
data['GeneticAlgorithm']['25.1'] = 4500
data['MIMIC']['25.1'] = 7050
data['SimulatedAnnealing']['25.2'] = 1436
data['GeneticAlgorithm']['25.2'] = 6500
data['MIMIC']['25.2'] = 3150
data['SimulatedAnnealing']['30.1'] = 1827
data['GeneticAlgorithm']['30.1'] = 28500
data['MIMIC']['30.1'] = 14350
data['SimulatedAnnealing']['30.2'] = 1558
data['GeneticAlgorithm']['30.2'] = 19750
data['MIMIC']['30.2'] = 14350

plotDistribution(data)

measures = ['bestvalue', 'bestoptimal']
names = ['SimulatedAnnealing', 'GeneticAlgorithm', 'MIMIC']

plots = []
labels = []
nlist = [10, 15, 20, 25, 30]

fig = plt.figure()
subplot = fig.add_subplot(111)

for name in names:
    evaluationList = []
    for n in nlist:
        evaluations = 0
        for i in [1, 2]:
            evaluations += data[name]['{0}.{1}'.format(n, i)]
        evaluations /= 2.
        evaluationList.append(evaluations)

    plots.append(subplot.plot(nlist, evaluationList)[0])
    labels.append(name)

font = FontProperties()
font.set_size('small')
plt.legend(plots, labels, loc='upper center', fancybox = True, ncol=2,  prop=font)

plt.savefig(args.plots + "/fourpeaks.png")

"""
