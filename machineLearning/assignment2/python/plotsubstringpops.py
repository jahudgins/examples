import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
import importlib
import sys
import pdb

from matplotlib.font_manager import FontProperties

data = [
    ['MIMIC', 100, 0.01, 70.0],
    ['GeneticAlgorithm', 100, 0.01, 70.0],
    ['MIMIC', 100, 0.02, 70.0],
    ['GeneticAlgorithm', 100, 0.02, 70.0],
    ['MIMIC', 100, 0.04, 70.0],
    ['GeneticAlgorithm', 100, 0.04, 69.0],
    ['MIMIC', 100, 0.10, 70.0],
    ['GeneticAlgorithm', 100, 0.10, 70.0],
    ['MIMIC', 100, 0.20, 70.0],
    ['GeneticAlgorithm', 100, 0.20, 70.0],
    ['MIMIC', 100, 0.40, 57.0],
    ['GeneticAlgorithm', 100, 0.40, 70.0],
    ['MIMIC', 100, 0.60, 58.0],
    ['GeneticAlgorithm', 100, 0.60, 70.0],
    ['MIMIC', 100, 0.70, 34.0],
    ['GeneticAlgorithm', 100, 0.70, 70.0],
    ['MIMIC', 100, 0.80, 31.0],
    ['GeneticAlgorithm', 100, 0.80, 19.0],
    ['MIMIC', 100, 0.90, 32.0],
    ['GeneticAlgorithm', 100, 0.90, 10.0],
    ['MIMIC', 200, 0.01, 70.0],
    ['GeneticAlgorithm', 200, 0.01, 70.0],
    ['MIMIC', 200, 0.02, 100.0],
    ['GeneticAlgorithm', 200, 0.02, 70.0],
    ['MIMIC', 200, 0.04, 100.0],
    ['GeneticAlgorithm', 200, 0.04, 70.0],
    ['MIMIC', 200, 0.10, 100.0],
    ['GeneticAlgorithm', 200, 0.10, 70.0],
    ['MIMIC', 200, 0.20, 70.0],
    ['GeneticAlgorithm', 200, 0.20, 100.0],
    ['MIMIC', 200, 0.40, 58.0],
    ['GeneticAlgorithm', 200, 0.40, 70.0],
    ['MIMIC', 200, 0.60, 30.0],
    ['GeneticAlgorithm', 200, 0.60, 70.0],
    ['MIMIC', 200, 0.70, 37.0],
    ['GeneticAlgorithm', 200, 0.70, 100.0],
    ['MIMIC', 200, 0.80, 36.0],
    ['GeneticAlgorithm', 200, 0.80, 70.0],
    ['MIMIC', 200, 0.90, 31.0],
    ['GeneticAlgorithm', 200, 0.90, 12.0],
    ['MIMIC', 400, 0.01, 70.0],
    ['GeneticAlgorithm', 400, 0.01, 69.0],
    ['MIMIC', 400, 0.02, 100.0],
    ['GeneticAlgorithm', 400, 0.02, 70.0],
    ['MIMIC', 400, 0.04, 70.0],
    ['GeneticAlgorithm', 400, 0.04, 70.0],
    ['MIMIC', 400, 0.10, 58.0],
    ['GeneticAlgorithm', 400, 0.10, 70.0],
    ['MIMIC', 400, 0.20, 48.0],
    ['GeneticAlgorithm', 400, 0.20, 70.0],
    ['MIMIC', 400, 0.40, 48.0],
    ['GeneticAlgorithm', 400, 0.40, 70.0],
    ['MIMIC', 400, 0.60, 46.0],
    ['GeneticAlgorithm', 400, 0.60, 70.0],
    ['MIMIC', 400, 0.70, 19.0],
    ['GeneticAlgorithm', 400, 0.70, 70.0],
    ['MIMIC', 400, 0.80, 37.0],
    ['GeneticAlgorithm', 400, 0.80, 70.0],
    ['MIMIC', 400, 0.90, 52.0],
    ['GeneticAlgorithm', 400, 0.90, 29.0],
    ['MIMIC', 800, 0.01, 70.0],
    ['GeneticAlgorithm', 800, 0.01, 70.0],
    ['MIMIC', 800, 0.02, 70.0],
    ['GeneticAlgorithm', 800, 0.02, 70.0],
    ['MIMIC', 800, 0.04, 90.0],
    ['GeneticAlgorithm', 800, 0.04, 70.0],
    ['MIMIC', 800, 0.10, 69.0],
    ['GeneticAlgorithm', 800, 0.10, 70.0],
    ['MIMIC', 800, 0.20, 74.0],
    ['GeneticAlgorithm', 800, 0.20, 70.0],
    ['MIMIC', 800, 0.40, 58.0],
    ['GeneticAlgorithm', 800, 0.40, 70.0],
    ['MIMIC', 800, 0.60, 58.0],
    ['GeneticAlgorithm', 800, 0.60, 70.0],
    ['MIMIC', 800, 0.70, 35.0],
    ['GeneticAlgorithm', 800, 0.70, 19.0],
    ['MIMIC', 800, 0.80, 33.0],
    ['GeneticAlgorithm', 800, 0.80, 22.0],
    ['MIMIC', 800, 0.90, 49.0],
    ['GeneticAlgorithm', 800, 0.90, 10.0],
]

for name in ['MIMIC', 'GeneticAlgorithm']:
    fig = plt.figure()
    subplot = fig.add_subplot(111)

    plots = []
    labels = []

    for population in [100, 200, 400, 800]:
        x = []
        y = []
        for d in data:
            if d[0] == name and d[1] == population:
                x.append(d[2])
                y.append(d[3])

        plots.append(subplot.plot(x, y)[0])
        labels.append("{0}".format(population))


    font = FontProperties()
    font.set_size('small')
    plt.legend(plots, labels, loc='lower center', fancybox = True, ncol=2,  prop=font)
    plt.savefig("plots/substringpop/{0}.png".format(name))

