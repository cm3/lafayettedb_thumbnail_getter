from docopt import docopt
import os
import os.path
import pandas as pd
from pyquery import PyQuery as pq
import urllib.parse
from requests import get
import sys
import time

__doc__ = """{f}

Based on input csv file, download image thumbnails and add a filename column to the csv file.
This script is not for general purpose. For crawling from digital.lafayette.edu.
output csv filename is automatically generated as <original>_with_thumbnails.csv .
output thumbnail filename is automatically generated based on DC.identifier.
output directory is automatically generated based on input csv file.

Usage:
    {f} <input_csv>
    {f} -h | --help

Options:
    -h --help                Show this screen and exit.
""".format(f=__file__)

def download(url, file_name, dirpath):
    # open in binary mode
    with open(dirpath+"/"+file_name, "wb") as file:
        response = get(url)
        file.write(response.content)

def main(input_csv):
    df = pd.read_csv(input_csv, header=0, encoding="utf-8")
    filename_head, ext = os.path.splitext(input_csv)
    outputcsv_path = filename_head+"_with_thumbnails.csv"
    outputdir_path = filename_head+"_thumbnails"
    if not os.path.exists(outputdir_path):
        os.mkdir(outputdir_path)

    filename_list = [""]*len(df) # initialize with the length of df
    for i, v in df.ix[:,'object_url'].iteritems():
        print(str(i)+": "+str(v))
        d = pq(url=v)
        # e.g.:
        # <meta property="og:image" content="https://digital.lafayette.edu/islandora/object/islandora:18709/datastream/JPG/view" />
        # https://digital.lafayette.edu/adore-djatoka/resolver?url_ver=Z39.88-2004&rft_id=http%3A%2F%2Fdigital.lafayette.edu%2Fislandora%2Fobject%2Fislandora%3A33760%2Fdatastream%2FJP2%2Fview&svc_id=info%3Alanl-repo%2Fsvc%2FgetRegion&svc_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajpeg2000&svc.level=1
        url = "https://digital.lafayette.edu/adore-djatoka/resolver?url_ver=Z39.88-2004&rft_id="+urllib.parse.quote(d("meta[property='og:image']").attr('content'), safe='').replace("https","http").replace("JPG","JP2")+"&svc_id=info%3Alanl-repo%2Fsvc%2FgetRegion&svc_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajpeg2000&svc.level=1"
        # <meta name="DC.identifier" content="islandora:18707" />
        filename = d("meta[name='DC.identifier']").attr('content').replace(":","")+".jpg"
        print(url)
        print(filename)
        download(url,filename,outputdir_path)
        filename_list[i] = filename
        time.sleep(3)
    df["thumbnail"] = filename_list
    df.to_csv(outputcsv_path, encoding="utf-8")

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args['<input_csv>'])
