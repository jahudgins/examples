To run mdp analysis:
    python basketball.py
    python buycar.py

Python package numpy must be installed.

Each program has various options. To see full list:
    python basketball.py --help

For more in-depth analysis use the '--analyze' option (takes longer time).

Generated output files:
    *.dot -- graph files to use with graphviz to generate images (including optimal policies)
        dot -Tpng <dot-file> -o <dot-file>.png
    *.utilities -- sorted list of all states and utilities


