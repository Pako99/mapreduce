import logging
import time
import numpy as np

from downloader import wgs_to_tile, get_url

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)



# ---------------------------------------------------------
if __name__ == '__main__':

   
    



    # Define the number of workers (N)
    N = 4
    matrix_size = 20
    # Calculate the size of each submatrix
    submatrix_size = 5

    subm_m_size = matrix_size/submatrix_size


    # Calculate the number of submatrices per worker
    submatrices_per_worker = (matrix_size // submatrix_size) * (matrix_size // submatrix_size) // N
    logger.info("matrix size= {ms} submatrix size= {sms}, workers= {wrks}, subm_work= {sbmw}".format(ms=matrix_size, sms=submatrix_size, wrks=N, sbmw=submatrices_per_worker))
    # Distribute submatrices among N workers
    workers_submatrices = []
    for worker_id in range(N):
        submatrix_batch = []
        for i in range(submatrices_per_worker):
            submatrix_id = i + submatrices_per_worker * worker_id
            subm_row = int(submatrix_id / subm_m_size)
            subm_col = int(submatrix_id % subm_m_size)
            start_row = int(subm_row * subm_m_size)
            start_col = int(subm_col * subm_m_size)
            submatrix = [start_row, start_col]
            submatrix_batch.append(submatrix)
        workers_submatrices.append(submatrix_batch)


    style='s'
    server="Google"
    with open("input2.txt", "w") as input_file:
        for worker_id, submatrix_batch in enumerate(workers_submatrices):
       
            for i, submatrix in enumerate(submatrix_batch):
                input_file.write(f"{submatrix}\n")

    # Print the submatrices assigned to each worker
    #for worker_id, submatrix_batch in enumerate(workers_submatrices):
        #print(f"Worker {worker_id + 1} Submatrices:")
        #for i, submatrix in enumerate(submatrix_batch):
            #print("Submatrix {i + 1}:")
            #print(submatrix)
           # urls = [get_url(server, i, j, z, style) for j in range(pos1y+submatrix[1], pos1y + submatrix[1]+submatrix_size) for i in range(pos1x+submatrix[0], pos1x + submatrix[0]+ submatrix_size)]
            #print (urls)
            #print()
