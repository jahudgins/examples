import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
import sys
import math
import json
import numpy

def loadJson(filename):
    f = open(filename, "rt")
    stats = json.load(f)
    f.close()
    return stats

def plotJson(stats, subplot, label, color, maxIterations):
    values =[]

    for key, stat in stats.items():
        value = []
        value.append(int(key))
        value.append(numpy.mean(stat))
        value.append(numpy.std(stat))
        values.append(value)

    values.sort()

    # stetch the last value all the way out so that we can see a baseline
    last = values[-1]
    values.append([maxIterations, last[1], last[2]])

    iterations = map(lambda x : x[0], values)
    means = map(lambda x : x[1], values)
    meansMinusStdDev = map(lambda x : x[1]-x[2], values)
    meansPlusStdDev = map(lambda x : x[1]+x[2], values)

    subplot.plot(iterations, means, lw=2, label=label, color=color)
    subplot.fill_between(iterations, meansPlusStdDev, meansMinusStdDev, facecolor=color, alpha=0.4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot graph of Reinforcement Learning.')
    parser.add_argument('--unknown', required=True, help='json file for unknown rewards')
    parser.add_argument('--known', required=True, help='json file for known rewards')
    parser.add_argument('--vi', required=True, help='json file for value iteration')
    parser.add_argument('--label', required=True, help='label for graph')
    args = parser.parse_args()

    fig = plt.figure()
    subplot = fig.add_subplot(111)

    unknownStats = loadJson(args.unknown)
    knownStats = loadJson(args.known)
    viStats = loadJson(args.vi)

    maxIterations = 0
    maxIterations = max(maxIterations, max(map(lambda x : int(x), unknownStats.keys())))
    maxIterations = max(maxIterations, max(map(lambda x : int(x), knownStats.keys())))
    maxIterations = max(maxIterations, max(map(lambda x : int(x), viStats.keys())))


    plotJson(unknownStats, subplot, 'Unknown Rewards', 'blue', maxIterations)
    plotJson(knownStats, subplot, 'Known Rewards', 'yellow', maxIterations)
    plotJson(viStats, subplot, 'Value Iteration', 'red', maxIterations)


    subplot.set_title('Simulated Reward for RL {0}'.format(args.label))
    #subplot.legend(loc='upper left')
    subplot.legend(loc='lower right')
    subplot.set_xlabel('iterations')
    subplot.set_ylabel('reward')
        

    plt.savefig('{0}.rl.png'.format(args.label))
