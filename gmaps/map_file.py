# -*- coding: utf-8 -*-
import logging
import time
import numpy as np
import json
from downloader import wgs_to_tile, get_url

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------
if __name__ == '__main__':
    start_time = time.time()
    out_err = open("bad_links.csv", "w")
    zone = 'test'
    maps = {'marcianise': [41.03699966153493, 14.282332207120104, 41.02356625889453, 14.300298406435248],
            'casapulla' : [41.082515040404, 14.268917099445803, 41.066324184008195, 14.302277371886024],
            'casagiove' : [41.08261546935178, 14.303388824263887, 41.07064562316231, 14.324267139938394],
            'capodrise' : [41.05162612435181, 14.288554711937884, 41.03859863125092, 14.311235472131052],
            'portico_caserta': [41.06655157598264, 14.26429436809843, 41.052507617894044, 14.29476426353296],
            'puglianello': [],
            'campania': [41.677007, 13.892689, 41.087208, 15.770957],
            'test': [41.047047, 14.282363, 41.029596, 14.326394],
            'melito ':[40.92771444067378, 14.219887933210089,40.925509564004884, 14.224179467277315],
            'orta' :[40.975746666849105, 14.268537979604302,40.97041639590007, 14.27352333271716]
            }

    c_map = maps['test' ]

    x1 = c_map[1]
    y1 = c_map[0]
    x2 = c_map[3]
    y2 = c_map[2]
    z = 18
    pos1x, pos1y = wgs_to_tile(x1, y1, z)
    pos2x, pos2y = wgs_to_tile(x2, y2, z)
    lenx = pos2x - pos1x + 1
    glob_lenx = lenx
    leny = pos2y - pos1y + 1
    logger.info("tiles from {pos1x},{pos1y}, [{lenx},{leny}]".format(pos1x=pos1x, pos1y=pos1y, lenx=lenx, leny=leny))

    matrix_size = 10
    # Calculate the size of each submatrix
    submatrix_size = 9

    matrix_size = matrix_size + (submatrix_size - (matrix_size % submatrix_size))

    subm_m_size = (matrix_size / submatrix_size)

    # Calculate the number of submatrices
    submatrices_number = (matrix_size // submatrix_size) * (matrix_size // submatrix_size)
    logger.info("matrix size= {ms} submatrix size= {sms}".format(ms=matrix_size, sms=submatrix_size))

    # Distribute submatrices among N workers
    outfile = open("mapper_input.txt", "w")

    for submatrix_id in range(submatrices_number):
        
        
        str_line = {'msize': matrix_size, 'subsize': submatrix_size, 'pos1x': pos1x, 'pos1y': pos1y}
        str_line['tiles_dir'] = submatrix_id
        str_line['server'] = "Google"
        str_line['style'] = 's'
        str_line['zoom'] = z
        subm_row = int(submatrix_id // (matrix_size // submatrix_size))
        subm_col = int(submatrix_id % (matrix_size // submatrix_size))
        start_row = int(subm_row * submatrix_size)
        start_col = int(subm_col * submatrix_size)
        str_line['start_row'] = start_row
        str_line['start_col'] = start_col
        outfile.write(json.dumps(str_line) + "\n")
        

    outfile.close()
