import argparse
import importlib
import sys
import pdb

def importFile(data, name):
    module = importlib.import_module(name)
    data[name] = eval("module.{0}".format(name))

parser = argparse.ArgumentParser(description='Plot graphs based on data from clustering experiments.')
parser.add_argument('--keepratio', required=True, help='directory to read files output by experiments')
parser.add_argument('--population', required=True, help='directory to read files output by experiments')
args = parser.parse_args()

directory = "svnignore/output/substringp{0}-k{1}".format(args.population, args.keepratio)
sys.path.append(directory)

data = {}

['bestvalue']
names = ['MIMIC', 'GeneticAlgorithm']

for name in names:
    importFile(data, name)
    bestvalueIndex = data[name]['trainlabels'].index('bestvalue')
    values = data[name]['train']
    print "['{0}', {1}, {2}, {3}]".format(name, args.population, args.keepratio, values[-1][bestvalueIndex])

