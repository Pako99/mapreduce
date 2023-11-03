
import cv2
from PIL import Image
import json
import sys
from io import BytesIO
import cv2
from hdfs import InsecureClient
import os
import shutil



hdfs_client = InsecureClient("http://node-master:50070")
hdfs_path="/home/spark/immagini/"


def savehdfs(immagine,hdfs_filename):
     try:
        
        
        if immagine is not None:
            
            with hdfs_client.write(hdfs_filename, overwrite=True) as writer:
               immagine.save(writer,format="TIFF")
         
        else: print("vuota")

     except Exception as e:
         # Gestisci gli errori durante la scrittura su HDFS
       print(f"Errore durante la scrittura dell'immagine su HDFS: {str(e)}")
    



def resize(infile: str, outfile: str):
    coff_resize = 62.5/90
    coff_pix = 9*256/1500
    # if this image is 2304 px 
    img=cv2.imread(infile)
    # this should be 1600px 1m per px
    img_75 = cv2.resize(img, (1500,1500), fx=coff_resize,fy=coff_resize)
    cv2.imwrite(outfile, img_75) 

def merge_tiles(pos1x, pos1y, lenx, leny, tiles_dir):
    width = lenx * 256
    height = leny * 256
    # Crea un'immagine vuota per il merge
    merged_image = Image.new('RGBA', (width, height))
    # Combina le tile nell'immagine risultante
    for y in range(leny):
        for x in range(lenx):
            with hdfs_client.read(f"{tiles_dir}/{pos1y+y}_{pos1x+x}_tile.jpeg") as reader:
                small_pic = Image.open(BytesIO(reader.read()))  # Corretta apertura dell'immagine
                merged_image.paste(small_pic, (x * 256, y * 256))
    print('Tiles merge completed')
    
    return merged_image

def final_merging(pos1x_list, pos1y_list, output_dir):
    # Calcola le dimensioni dell'immagine finale
    width = len(pos1x_list) * 1500
    height = len(pos1y_list) * 1500
    
    # Crea un'immagine vuota per il merging finale
    merged_image = Image.new('RGB', (width, height))
    
    i = 0
    while i < len(pos1y_list):
        j = 0
        while j < len(pos1x_list):
            # Costruisci il percorso del file immagine
            image_path = f"{output_dir}/{pos1x_list[j]}_{pos1y_list[i]}_1500.tiff"
            
            # Verifica se il file esiste prima di caricarlo
            if os.path.exists(image_path):
                small_pic = Image.open(image_path)
                
                # Calcola gli indici di paste in base alle posizioni relative
                x_offset = j * 1500
                y_offset = i * 1500
                
                # Incolla l'immagine nell'immagine finale
                merged_image.paste(small_pic, (x_offset, y_offset))
            else:
                # Il file non esiste, passa al prossimo ciclo senza incrementare i e j
                j += 1
                continue
            
            j += 1
        i += 1
            
    # Salva l'immagine finale
    return merged_image

output_dir = "/home/spark/immagini/"
merging=False
pos1x_list=[]
pos1y_list=[]

if __name__ == "__main__":
    for line in sys.stdin: 
        

        json_str =json.loads(line)
        group=json_str['group']
        #hdfs_client.makedirs( f"{hdfs_path}/{group}", permission=755) #da verificare correttezza
        if 'bool' in json_str:
            merging =json_str['bool']
        else:
            pass
        # Estrai le informazioni dalla prima tile per inizializzare il merge
        group=json_str['group']

        start_col = json_str["start_col"]
        end_col = start_col+json_str["subsize"]
        start_row = json_str["start_row"]
        end_row = start_row+json_str["subsize"]
        lenx = end_row-start_row
        leny = end_col-start_col
        pos1x = json_str['pos1x'] + start_row
        pos1y = json_str['pos1y'] + start_col
        outpic = merge_tiles(pos1x, pos1y, lenx, leny, json_str['tiles_dir'])
        if not os.path.exists(f"{output_dir}/{group}"):
            os.makedirs(f"{output_dir}/{group}")
        outpic = outpic.convert('RGB')
        x_pos=(int)(pos1x-json_str["pos1x"])/lenx
        y_pos=(int)(pos1y-json_str["pos1y"])/leny
        outpic.save(f"{output_dir}/{group}/{pos1x}_{pos1y}_{lenx}.tiff", format="TIFF")
        resize(f"{output_dir}/{pos1x}_{pos1y}_{lenx}.tiff",f"{output_dir}/{group}/{x_pos}_{y_pos}_1500.tiff")
        #rete neurale per generare la mask image 
        if x_pos not in pos1x_list:
            
          pos1x_list.append(x_pos)
        if y_pos not in pos1y_list: 
         pos1y_list.append(y_pos)
        #immagine=Image.open(f"{output_dir}/{group}/{x_pos}_{y_pos}_1500.tiff")
        #savehdfs(immagine,f"{output_dir}/{group}/{x_pos}_{y_pos}_1500.tiff")
        os.remove(f"{output_dir}/{group}/{pos1x}_{pos1y}_{lenx}.tiff")
            
        if(merging):
           
           
           
           
            
           final_merge=final_merging(pos1x_list,pos1y_list,f"{output_dir}/{group}")#merging mask image
          
           final_merge.save(f"{output_dir}/{group}/final.tiff",format="TIFF")
           #algoritmo genetico 
          # savehdfs(hdfs_path,f"{output_dir}/{group}/final.tiff")
           pos1x_list.clear()
           pos1y_list.clear()
           merging=False
            
        else:
            pass
       
       