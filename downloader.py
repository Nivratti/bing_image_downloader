import os, sys
import shutil
from pathlib import Path
import pandas as pd
import urllib
import configparser


try:
    from bing import Bing
except ImportError:  # Python 3
    from .bing import Bing


def download(query, limit=100, output_dir='dataset', adult_filter_off=False, 
force_replace=False, timeout=60, verbose=True, filters=''):

    # engine = 'bing'
    if adult_filter_off:
        adult = 'off'
    else:
        adult = 'on'

    
    image_dir = Path(output_dir).joinpath(query).absolute()

    if force_replace:
        if Path.isdir(image_dir):
            shutil.rmtree(image_dir)

    # check directory and create if necessary
    try:
        if not Path.is_dir(image_dir):
            Path.mkdir(image_dir, parents=True)

    except Exception as e:
        print('[Error]Failed to create directory.', e)
        sys.exit(1)
        
    print("[%] Downloading Images to {}".format(str(image_dir.absolute())))
    bing = Bing(query, limit, image_dir, adult, timeout, filters, verbose)
    bing.run()

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")
  
def main():

    config = configparser.RawConfigParser()
    config.read('filters.cfg')

    details_dict = dict(config.items('settings'))
    # print(f"details_dict: ", details_dict)

    task_filename = "task_list.xlsx"
    df = pd.read_excel(task_filename)
    # df.head()

    for index, row in df.iterrows():
        task_name = row["task_name"]
        limit = row["image_download_count"]
        height = row["minimum_height"]
        width = row["minimum_width"]

        print("=" * 30)
        print(f"task_name: ", task_name)
        print(f"limit: ", limit)
        print(f"height: ", height)
        print(f"width: ", width)
        
        # flag to store filters
        filters = ""
        ## if face only images to download
        if "face_only" in details_dict:
            if str2bool(details_dict["face_only"]):
                filters = "filterui:face-face"

        params = {
            "query": task_name,
        }

        if limit:
            params["limit"] = limit

        if not pd.isna(height) and not pd.isna(width):
            filters += f" filterui:imagesize-custom_{height}_{width}"
        else:
            if "imagesize" in details_dict:
                if details_dict["imagesize"] == "wallpaper":
                    filters += f" filterui:imagesize-wallpaper"

        print(f"filters: ", filters)

        # urllib.parse.quote_plus("filterui:face-face filterui:imagesize-custom_380_380")
        filters_url_quoted = urllib.parse.quote_plus(filters)

        params["filters"] = filters_url_quoted

        ## call download
        download(**params)


if __name__ == '__main__':
    main()
    # download('dog', output_dir="..\\Users\\cat", limit=10, timeout=1)
