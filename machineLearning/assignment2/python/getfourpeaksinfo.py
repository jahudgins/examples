import argparse
import importlib
import sys
import math
import pdb

def importFile(data, name):
    module = importlib.import_module(name)
    data[name] = eval("module.{0}".format(name))

parser = argparse.ArgumentParser(description='Plot graphs based on data from clustering experiments.')
parser.add_argument('--suffix', required=True, help='directory to read files output by experiments')
args = parser.parse_args()


data = {}

# plotDistribution(data)

names = ['SimulatedAnnealing', 'GeneticAlgorithm', 'MIMIC']

pydir = "output/fourpeaks-length{0}".format(args.suffix)
sys.path.append(pydir)
for name in names:
    importFile(data, name)
    print "data['{0}']['{1}'] = {2}".format(name, args.suffix, data[name]['train'][-1][1])
