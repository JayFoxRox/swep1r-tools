import argparse
import os


def ensure_folder_exists(folder):
    os.makedirs(folder, exist_ok=True)
    return folder


parser = argparse.ArgumentParser('SWE1R scripts ')
parser.add_argument('--out', help='directory where the output files are written', default='output', type=ensure_folder_exists)
parser.add_argument('input', help='input file')

multiparser = argparse.ArgumentParser('SWE1R scripts ')
multiparser.add_argument('input', nargs='+', help='input files')