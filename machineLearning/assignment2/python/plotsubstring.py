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
    x = range(len(values))

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

plotDistribution(data)

measures = ['bestvalue', 'bestoptimal']
names = ['SimulatedAnnealing', 'GeneticAlgorithm', 'MIMIC']



"""
names = []
for i in range(1, 8):
    names.append('sa{0}'.format(int(math.pow(2, i))))

temps = [[], []]
for i in range(1, 6):
    temps[0].append('sa{0}'.format(int(math.pow(2, i))))
for i in range(7, 8):
    temps[1].append('sa{0}'.format(int(math.pow(2, i))))
measure = 'bestvalue'
"""

for name in names:
    importFile(data, name)

pngs = ['set0', 'set1']
for measure in measures:
# for temp, png in zip(temps, pngs):

    # use these for measures
    png = measure
    temp = names

    fig = plt.figure()
    subplot = fig.add_subplot(111)

    plots = []
    labels = []
    plotTags = ['evaluations', measure]

    for name in temp:
        #print measure, name
        print name
        plotTraining(data, subplot, plotTags, name, plots, labels)

    max= data['distribution']['max']
    x = [0, 50000]
    y = [max, max]
    plots.append(subplot.plot(x, y)[0])
    labels.append("max")

    font = FontProperties()
    font.set_size('small')
    plt.legend(plots, labels, loc='lower center', fancybox = True, ncol=2,  prop=font)

    plt.ylim([0, int(max*1.1)])

    plt.savefig(args.plots + "/" + png + ".png")

