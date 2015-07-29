__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

import os
import global_variables as gv
from lib import tools


if __name__=='__main__':

    files_path = os.path.join(gv.project_data_path, 'Archea/genes_and_flanks/win_10/pty//')

    neighborhoods = tools.load_neighborhoods(files_path)
    