import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
import importlib
import sys
import pdb

from matplotlib.font_manager import FontProperties


def plotTraining(data, subplot, name):
    importFile(data, name)
    values = data[name]['train']

    x = []
    y = []
    for value in values:
        x.append(value[1])
        y.append(value[2])

    plot = subplot.plot(x, y)[0]
    return plot

def importFile(data, name):
    module = importlib.import_module(name)
    data[name] = eval("module.{0}".format(name))

parser = argparse.ArgumentParser(description='Plot graphs based on data from clustering experiments.')
parser.add_argument('--directory', required=True, help='directory to read files output by experiments')
parser.add_argument('--plots', required=True, help='directory to write plots')
args = parser.parse_args()

sys.path.append(args.directory)

data = {}

evaluators = ['Best', 'BestIfStopped', 'CorrectCountEnd', 'SumCorrect']

gaChildren = ['oneChild']
#gaCrossover = ['Single']
gaChildrenLabels = ['Kid1']
#gaCrossoverLabels = ['S']

##gaChildren = ['twoChildren', 'oneChild']
#gaCrossover = ['Single', 'SingleStep3', 'TwoPoint', 'TwoPointStep3', 'Uniform', 'UniformStep3',]
##gaChildrenLabels = ['Kid2', 'Kid1']
#gaCrossoverLabels = ['S', 'Ss3', '2pt', '2pt3', 'Uni', 'Uni3',]

gaCrossover = ['SingleStep3', 'TwoPointStep3', 'UniformStep3',]
gaCrossoverLabels = ['Ss3', '2pt3', 'Uni3',]

#gaCrossover = ['Single', 'TwoPoint', 'Uniform']
#gaCrossoverLabels = ['S', '2pt', 'Uni']

solveStats = {}
solveAxis = evaluators + ['mimic'] + ['sa'] + gaChildren + gaCrossover
for solveTag in solveAxis:
    solveStats[solveTag] = [0, 0]

def updateSolveStat(data, solveStats, name, tags):
    for tag in tags:
        solveStats[tag][1] += 1
        if data[name]['solves'] == 'True':
            solveStats[tag][0] += 1


for evaluator in evaluators:
    print evaluator
    fig = plt.figure()
    subplot = fig.add_subplot(111)
    plots = []
    labels = []

    name = 'mimic_' + evaluator
    labels.append('mimic')
    plots.append(plotTraining(data, subplot, name))
    updateSolveStat(data, solveStats, name, [evaluator, 'mimic'])

    name = 'sa_' + evaluator
    labels.append('sa')
    plots.append(plotTraining(data, subplot, name))
    updateSolveStat(data, solveStats, name, [evaluator, 'sa'])

    for crossover, crossoverLabel in zip(gaCrossover, gaCrossoverLabels):
        for children, childLabel in zip(gaChildren, gaChildrenLabels):
            name = 'ga_' + evaluator + crossover + '_' + children
            labels.append('ga'+crossoverLabel+childLabel)
            plots.append(plotTraining(data, subplot, name))
            updateSolveStat(data, solveStats, name, [evaluator, crossover, children])

    font = FontProperties()
    font.set_size('small')
    plt.legend(plots, labels, loc='lower center', fancybox = True, ncol=2,  prop=font)

    plt.savefig(args.plots + "/" + evaluator + ".png")

print "Success rate for various axis"
for solveTag in solveAxis:
    print "{0}:{1}".format(solveTag, float(solveStats[solveTag][0]) / solveStats[solveTag][1])
print

    

