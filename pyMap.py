import os
import sys
import math
import requests
from PIL import Image
from tqdm import trange

url = {
    "gaode": "http://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x=%i&y=%i&z=%i",
    "gaode.image": "http://webst02.is.autonavi.com/appmaptile?style=6&x=%i&y=%i&z=%i",
    "tianditu": "http://t1.tianditu.cn/DataServer?T=vec_w&X=%i&Y=%i&L=%i"
}


def process_latlng(north, west, south, east, zoom, output='output/mosaic.png', maptype="gaode.image"):
    """
    download and mosaic by latlng

    Keyword arguments:
    north -- north latitude
    west  -- west longitude
    south -- south latitude
    east  -- east longitude
    zoom  -- map scale (0-18)
    output -- output file name default output/mosaic.png

    """
    left, top = latlng2tilenum(north, west, zoom)
    right, bottom = latlng2tilenum(south, east, zoom)
    process_tilenum(left, right, top, bottom, zoom, output, maptype)


def process_tilenum(left, right, top, bottom, zoom, output='output/mosaic.png', maptype="gaode.image"):
    """
    download and mosaic by tile number

    Keyword arguments:
    left   -- left tile number
    right  -- right tile number
    top    -- top tile number
    bottom -- bottom tile number
    zoom   -- map scale (0-18)
    output -- output file name default output/mosaic.png

    """
    download(left, right, top, bottom, zoom, maptype)
    _mosaic(left, right, top, bottom, zoom, output)


def download(left, right, top, bottom, zoom, maptype="gaode.image"):
    for x in trange(left, right + 1):
        for y in trange(top, bottom + 1):
            path = './tiles/%i/%i/%i.png' % (zoom, x, y)
            if not os.path.exists(path):
                _download(x, y, zoom, maptype)


def _download(x, y, z, maptype="gaode.image"):
    map_url = url[maptype] % (x, y, z)

    r = requests.get(map_url)
    path = './tiles/%i/%i' % (z, x)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open('%s/%i.png' % (path, y), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()


def _mosaic(left, right, top, bottom, zoom, output='output/mosaic.png'):
    size_x = (right - left + 1) * 256
    size_y = (bottom - top + 1) * 256
    output_im = Image.new("RGBA", (size_x, size_y))

    for x in trange(left, right + 1):
        for y in trange(top, bottom + 1):
            path = './tiles/%i/%i/%i.png' % (zoom, x, y)
            target_im = Image.open(path)
            output_im.paste(target_im, (256 * (x - left), 256 * (y - top)))
    output_path = os.path.split(output)
    if len(output_path) > 1 and len(output_path) != 0:
        if not os.path.isdir(output_path[0]):
            os.makedirs(output_path[0])
    output_im.save(output)


def latlng2tilenum(lat_deg, lng_deg, zoom):
    """
    convert latitude, longitude and zoom into tile in x and y axis
    referencing http://www.cnblogs.com/Tangf/archive/2012/04/07/2435545.html

    Keyword arguments:
    lat_deg -- latitude in degree
    lng_deg -- longitude in degree
    zoom    -- map scale (0-18)

    Return two parameters as tile numbers in x axis and y axis
    """
    n = math.pow(2, int(zoom))
    xtile = ((lng_deg + 180) / 360) * n
    lat_rad = lat_deg / 180 * math.pi
    ytile = (1 - (math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi)) / 2 * n
    return math.floor(xtile), math.floor(ytile)


def test():
    process_latlng(22.4566710000, 113.8899620000, 22.3455760000, 114.2126860000, 13, 'output/houmen.png', "gaode")


def cml():
    if not len(sys.argv) in [7, 8]:
        print('input 7 parameter northeast latitude,northeast longitude, southeast latitude, southeast longitude,zoom , output file, map type like gaode')
        return
    process_latlng(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), str(sys.argv[6]), str(sys.argv[7]))

if __name__ == '__main__':
    test()
    # cml()
