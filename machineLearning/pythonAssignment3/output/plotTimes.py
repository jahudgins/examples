import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
import sys
import math
import re
import json

def loadJson(filename):
    f = open(filename, "rt")
    stats = json.load(f)
    f.close()
    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot graph for iteration times Value/Policy Iteration.')
    args = parser.parse_args()

    f = open("basketball.itertimes.txt", "rt")
    lines = f.readlines()
    f.close()

    stats = {   'value': [],
                'policy': [] }

    for line in lines:
        m = re.match(r'(?P<type>\w*)Iteration iterations:(?P<iterations>\w*), states:(?P<states>\w*), elapsed:(?P<elapsed>[0-9.]*)', line)
        if m:
            l = []
            for key in ['states', 'iterations', 'elapsed']:
                l.append(float(m.group(key)))
            stats[m.group('type')].append(l)

    stats['value'].sort()
    stats['policy'].sort()

    valueStates, valueIterations, valueElapsed = zip(*stats['value'])
    policyStates, policyIterations, policyElapsed = zip(*stats['policy'])

    buycar = loadJson('buycar.itertimes.json')
    iterTypes = ['VI', 'PI']
    tags = ['numstates', 'iterations', 'elapsed']
    buycarStats = {}
    for iterType in iterTypes:
        buycarStats[iterType] = {}
        for tag in tags:
            buycarStats[iterType][tag] = []

    for b in buycar:
        for iterType in iterTypes:
            for tag in tags:
                buycarStats[iterType][tag].append(b[iterType][tag])

    basketballVi = loadJson('basketball.2.viitertimes.json')
    iterTypes = ['VI']
    tags = ['numstates', 'iterations', 'elapsed']
    vionly = {}
    for iterType in iterTypes:
        vionly[iterType] = {}
        for tag in tags:
            vionly[iterType][tag] = []

    for b in basketballVi:
        for iterType in iterTypes:
            for tag in ['numstates', 'iterations', 'elapsed']:
                vionly[iterType][tag].append(b[iterType][tag])



    fig = plt.figure()
    subplot = fig.add_subplot(111)

    subplot.plot(valueStates, valueElapsed, label='Baketball VI', color='blue')
    subplot.plot(policyStates, policyElapsed, label='Basketball PI', color='red')
    subplot.plot(buycarStats['VI']['numstates'], buycarStats['VI']['elapsed'], label='BuyCar VI', color='green')
    subplot.plot(buycarStats['PI']['numstates'], buycarStats['PI']['elapsed'], label='BuyCar PI', color='goldenrod')

    subplot.set_title('MDP Elapsed Time')
    subplot.legend(loc='upper left')
    subplot.set_xlabel('states')
    subplot.set_ylabel('elapsed time')

    plt.xlim([0,2500])
    plt.ylim([0,60])
    plt.savefig('elapsed.png')


    fig = plt.figure()
    subplot = fig.add_subplot(111)

    subplot.plot(valueStates, valueIterations, label='Basketball VI', color='blue')
    subplot.plot(policyStates, policyIterations, label='Basketball PI', color='red')
    subplot.plot(buycarStats['VI']['numstates'], buycarStats['VI']['iterations'], label='BuyCar VI', color='green')
    subplot.plot(buycarStats['PI']['numstates'], buycarStats['PI']['iterations'], label='BuyCar PI', color='goldenrod')

    subplot.set_title('MDP Iterations')
    subplot.legend(loc='upper left')
    subplot.set_xlabel('states')
    subplot.set_ylabel('iterations to solve')

    plt.xlim([0,2500])
    plt.savefig('iterations.png')


    fig = plt.figure()
    subplot = fig.add_subplot(111)

    subplot.plot(valueStates, valueElapsed, label='Baketball VI', color='blue')
    subplot.plot(buycarStats['VI']['numstates'], buycarStats['VI']['elapsed'], label='BuyCar VI', color='green')

    subplot.set_title('MDP Elapsed VI Only')
    subplot.legend(loc='upper left')
    subplot.set_xlabel('states')
    subplot.set_ylabel('elapsed time')

    plt.xlim([0,2500])
    plt.ylim([0,1.5])
    plt.savefig('elapsedVIonly.png')


    fig = plt.figure()
    subplot = fig.add_subplot(111)

    subplot.plot(vionly['VI']['numstates'], vionly['VI']['iterations'], label='Basketball Iterations', color='blue')
    subplot.plot(vionly['VI']['numstates'], vionly['VI']['elapsed'], label='Basketball Elapsed', color='green')

    subplot.set_title('MDP Basketball Longterm VI')
    subplot.legend(loc='upper left')
    subplot.set_xlabel('states')
    subplot.set_ylabel('time/iterations')

    plt.xlim([0,22500])
    #plt.ylim([0,1.5])
    plt.savefig('bblongterm.png')


