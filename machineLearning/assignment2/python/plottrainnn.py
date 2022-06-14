import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
import importlib
import sys
import pdb

from matplotlib.font_manager import FontProperties


def plotTraining(data, subplot, tags, name, plots, labels):
    xIndex = data[name]['trainlabels'].index(tags[0])
    yIndex = data[name]['trainlabels'].index(tags[1])
    values = data[name]['train']

    x = []
    y = []
    for value in values:
        x.append(value[xIndex])
        y.append(value[yIndex])

    plots.append(subplot.plot(x, y)[0])
    labels.append(name)

def importFile(data, name):
    module = importlib.import_module(name)
    data[name] = eval("module.{0}".format(name))

parser = argparse.ArgumentParser(description='Plot graphs based on data from clustering experiments.')
parser.add_argument('--directory', required=True, help='directory to read files output by experiments')
parser.add_argument('--plots', required=True, help='directory to write plots')
args = parser.parse_args()

sys.path.append(args.directory)

data = {}

measures = ['fitness', 'bestfitness', 'trainCorrect', 'testCorrect']
names = ['HillClimbRandomAll', 'HillClimbConverge', 'HillClimbRoundRobinDim', 'SimulatedAnnealing', 'GeneticAlgorithm']

for name in names:
    importFile(data, name)

for measure in measures:
    fig = plt.figure()
    subplot = fig.add_subplot(111)

    plots = []
    labels = []
    plotTags = ['evaluations', measure]

    for name in names:
        print measure, name
        plotTraining(data, subplot, plotTags, name, plots, labels)

    font = FontProperties()
    font.set_size('small')
    plt.legend(plots, labels, loc='lower center', fancybox = True, ncol=2,  prop=font)

    plt.savefig(args.plots + "/" + measure + ".png")

