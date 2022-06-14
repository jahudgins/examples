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

def autolabel(rects, heights):
    # attach some text labels
    for rect, height in zip(rects, heights):
        subplot.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha='center', va='bottom')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot graph for iteration times Value/Policy Iteration.')
    args = parser.parse_args()

    f = open("basketballCompare.txt", "rt")
    lines = f.readlines()
    f.close()

    stats = {}
    for line in lines:
        m = re.match(r'(?P<home>[^ ]*) vs (?P<away>[^ ]*) .*mean:(?P<mean>[^,]*), std.dev:(?P<stddev>\w*)', line)
        if m:
            if not stats.has_key(m.group('away')):
                stats[m.group('away')] = []
            stats[m.group('away')].append([float(m.group('mean')), float(m.group('stddev'))])

    fig = plt.figure()
    subplot = fig.add_subplot(111)

    algTypes = ['RLU', 'RLK', 'VI', 'Random']
    colors = ['blue', 'green', 'red', 'cyan']
    totalWidth = 0.8
    # offsetWidth = 0.15
    # width = totalWidth - offsetWidth * (len(algTypes) - 1)
    offsetWidth = width = totalWidth / len(algTypes)
    rects = []
    i = 0
    for algType, color in zip(algTypes, colors):
        ind = map(lambda x : x + offsetWidth * i, range(len(algTypes)))
        means = [mean for mean,std in stats[algType]]
        stddevs = [std for mean,std in stats[algType]]
        rects.append(subplot.bar(ind, means, width, color=color, yerr=stddevs, alpha=0.5))
        autolabel(rects[-1], means)
        i += 1

    subplot.legend(rects, map(lambda x : 'Away:' + x, algTypes))

    subplot.set_ylabel('Expected Reward')
    subplot.set_xlabel('Home Algorithm')
    subplot.set_title('Basketball Home vs Away Algorithm Comparison')
    subplot.set_xticks(map(lambda x : x + 0.4, range(len(algTypes))))
    subplot.set_xticklabels(algTypes)

    # plt.xlim([0,2500])
    plt.ylim([-250,750])
    plt.savefig('basketballCompare.png')

