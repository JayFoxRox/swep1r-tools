import argparse

parser = argparse.ArgumentParser('SWE1R scripts ')
parser.add_argument('--out', description='directory where the output files are written', default='/tmp/swep1r')
parser.add_argument('input', description='input file')

multiparser = argparse.ArgumentParser('SWE1R scripts ')
multiparser.add_argument('input', nargs='+', description='input files')