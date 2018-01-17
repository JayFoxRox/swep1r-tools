import argparse

parser = argparse.ArgumentParser('SWE1R scripts ')
parser.add_argument('--out', help='directory where the output files are written', default='/tmp/swep1r')
parser.add_argument('input', help='input file')

multiparser = argparse.ArgumentParser('SWE1R scripts ')
multiparser.add_argument('input', nargs='+', help='input files')