# -*- coding: utf-8 -*-

import sys
import os
import urllib.request as ur
from hdfs import InsecureClient
from downloader import wgs_to_tile,get_url
import numpy as np


hdfs_client = InsecureClient("http://master:50070")

def calcolamatrice():
 
 out_err = open("bad_links.csv", "w")
 zone = 'test'
 maps = {'marcianise': [41.03699966153493, 14.282332207120104, 41.02356625889453, 14.300298406435248],
         'casapulla' : [41.082515040404, 14.268917099445803, 41.066324184008195, 14.302277371886024],
         'casagiove' : [41.08261546935178, 14.303388824263887, 41.07064562316231, 14.324267139938394],
         'capodrise' : [41.05162612435181, 14.288554711937884, 41.03859863125092, 14.311235472131052],
         'portico_caserta': [41.06655157598264, 14.26429436809843, 41.052507617894044, 14.29476426353296],
         'puglianello': [],
         'campania': [41.677007, 13.892689, 41.087208, 15.770957],
         'test': [41.047047, 14.282363, 41.029596, 14.326394]
         }

 

 c_map = maps[zone]

 x1 = c_map[1]
 y1 = c_map[0]
 x2 = c_map[3]
 y2 = c_map[2]
 z = 17
 pos1x, pos1y = wgs_to_tile(x1, y1, z)
 pos2x, pos2y = wgs_to_tile(x2, y2, z)
 lenx = pos2x - pos1x + 1
 glob_lenx = lenx
 leny = pos2y-pos1y +1
 style='s'
 server="Google"
 tile_matrix = np.empty((leny, lenx), dtype=object)

 for j in range(pos1y, pos1y + leny):
        for i in range(pos1x, pos1x + lenx):

            tile_matrix[j - pos1y, i - pos1x] = get_url(server, i, j, z, style)
 
 return tile_matrix

downloaded_urls = set()


def download_and_save_image(url):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68'}

    header = ur.Request(url, headers=HEADERS)
    err = 0
    while (err < 3):
        try:
            image_data = ur.urlopen(header).read()
            filename = os.path.basename(url) + '.jpg'  # Aggiungi l'estensione .jpg al nome del file

            # Verifica se l'URL � gi� stato scaricato prima di procedere
            if url not in downloaded_urls:
                hdfs_client.write(filename, image_data, overwrite=True)
                downloaded_urls.add(url)
                sys.stderr.write(f"Scaricato {filename} e salvato su HDFS\n")
            else:
                sys.stderr.write(f"tile gia scaricata,salta.\n")

            return
        except Exception as e:
            err += 1
            sys.stderr.write(f"Error downloading {url}: {str(e)}\n")
    
    sys.stderr.write(f"download fallito {url}\n")
    


tile_matrix = calcolamatrice()

# Leggi le coordinate della sottomatrice dall'input
for line in sys.stdin:
    line = line.strip()
    if line.startswith("[") and line.endswith("]"):
        # Rimuovi le parentesi quadre iniziali e finali
        line = line[1:-1]

        # Estrai i due valori tra le virgole
        parts = line.split(',')
    start_row, start_col = map(int, line.split(','))

    # Estrai gli URL dalla sottomatrice 5x5
    submatrix = tile_matrix[start_row:start_row+5, start_col:start_col+5]

    # Scarica e salva i tile corrispondenti in HDFS
    for row in range(5):
        for col in range(5):
            url = submatrix[row, col]
            if url:
                download_and_save_image(url)




