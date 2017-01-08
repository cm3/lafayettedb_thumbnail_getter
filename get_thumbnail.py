from docopt import docopt
import os
import os.path
import pandas as pd
from pyquery import PyQuery as pq
import urllib.parse
from requests import get, exceptions
import sys
import time
import math

__doc__ = """{f}

- Based on input csv file, download image thumbnails and add a filename column to the csv file.
- This script is not for general purpose but for crawling from digital.lafayette.edu.
- Output thumbnail filename is automatically generated based on DC.identifier.
- Output directory is automatically generated based on input csv file.
- If there are values in thumbnail columns already, skip those rows.
This function enable users to continue download thumbnails when the connection is aborted.

Usage:
    {f} <csv>
    {f} -h | --help

Options:
    -h --help                Show this screen and exit.
""".format(f=__file__)

def download(url, file_name, dirpath):
    # open in binary mode
    with open(dirpath+"/"+file_name, "wb") as file:
        response = get(url)
        file.write(response.content)

def main(csv):
    df = pd.read_csv(csv, header=0, encoding="utf-8", dtype={"thumbnail":"str"})
    if not "thumbnail" in list(df.columns.values): # create thumbnail column if not there
        df["thumbnail"] = [""]*len(df)
        # df should be reconstructed for correct pd.isnull(v["thumbnail"]) distinction
        df.to_csv(csv, encoding="utf-8", index=False)
        df = pd.read_csv(csv, header=0, encoding="utf-8", dtype={"thumbnail":"str"})
    outputdir_path, ext = os.path.splitext(csv)
    if not os.path.exists(outputdir_path): # create directory if not there
        os.mkdir(outputdir_path)
    for i, v in df.iterrows():
        if pd.isnull(v["thumbnail"]):
            print(str(i))
            try:
                d = pq(url=v["object_url"])
            except:
                df.to_csv(csv, encoding="utf-8", index=False)
                raise ConnectionError("error on : "+v["object_url"]+" (html)")
            # e.g.:
            # <meta property="og:image" content="https://digital.lafayette.edu/islandora/object/islandora:18709/datastream/JPG/view" />
            # https://digital.lafayette.edu/adore-djatoka/resolver?url_ver=Z39.88-2004&rft_id=http%3A%2F%2Fdigital.lafayette.edu%2Fislandora%2Fobject%2Fislandora%3A33760%2Fdatastream%2FJP2%2Fview&svc_id=info%3Alanl-repo%2Fsvc%2FgetRegion&svc_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajpeg2000&svc.level=1
            url = "https://digital.lafayette.edu/adore-djatoka/resolver?url_ver=Z39.88-2004&rft_id="+urllib.parse.quote(d("meta[property='og:image']").attr('content'), safe='').replace("https","http").replace("JPG","JP2")+"&svc_id=info%3Alanl-repo%2Fsvc%2FgetRegion&svc_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajpeg2000&svc.level=1"
            # <meta name="DC.identifier" content="islandora:18707" />
            filename = d("meta[name='DC.identifier']").attr('content').split(",")[0].replace(":","")+".jpg"
            try:
                download(url,filename,outputdir_path)
                df.loc[i, 'thumbnail'] = filename
            except:
                df.to_csv(csv, encoding="utf-8", index=False)
                print(url)
                print(filename)
                raise ConnectionError("error on : "+v["object_url"]+" (jpg)")
            time.sleep(1)
    df.to_csv(csv, encoding="utf-8", index=False)

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args['<csv>'])
