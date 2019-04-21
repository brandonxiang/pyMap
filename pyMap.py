"""
github: https://github.com/brandonxiang/pyMap
license: MIT
"""
import os
import sys
import math
import requests
from PIL import Image
from tqdm import trange
import configparser

URL = {
    "gaode": "http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}",
    "gaode.image": "http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
    "tianditu": "http://t2.tianditu.cn/DataServer?T=vec_w&X={x}&Y={y}&L={z}",
    "googlesat": "http://khm0.googleapis.com/kh?v=203&hl=zh-CN&&x={x}&y={y}&z={z}",
    "tianditusat":"http://t2.tianditu.gov.cn/DataServer?T=img_w&X={x}&Y={y}&L={z}&tk=2ce94f67e58faa24beb7cb8a09780552",
    "esrisat":"http://server.arcgisonline.com/arcgis/rest/services/world_imagery/mapserver/tile/{z}/{y}/{x}",
    "gaode.road": "http://webst02.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scale=1&style=8",
    "default":"http://61.144.226.124:9001/map/GISDATA/WORKNET/{z}/{y}/{x}.png",
    "szbuilding":"http://61.144.226.124:9001/map/GISDATA/SZBUILDING/{z}/{y}/{x}.png",
    "szbase":"http://61.144.226.44:6080/arcgis/rest/services/basemap/szmap_basemap_201507_01/MapServer/tile/{z}/{y}/{x}"
}


def process_latlng(north, west, south, east, zoom, output='mosaic', maptype="default"):
    """
    download and mosaic by latlng

    Keyword arguments:
    north -- north latitude
    west  -- west longitude
    south -- south latitude
    east  -- east longitude
    zoom  -- map scale (0-18)
    output -- output file name default mosaic

    """
    north = float(north)
    west = float(west)
    south = float(south)
    east = float(east)
    zoom = int(zoom)
    assert(east>-180 and east<180)
    assert(west>-180 and west<180)
    assert(north>-90 and north<90)
    assert(south>-90 and south<90)
    assert(west<east)
    assert(north>south)

    left, top = latlng2tilenum(north, west, zoom)
    right, bottom = latlng2tilenum(south, east, zoom)
    process_tilenum(left, right, top, bottom, zoom, output, maptype)


def process_tilenum(left, right, top, bottom, zoom, output='mosaic', maptype="default"):
    """
    download and mosaic by tile number

    Keyword arguments:
    left   -- left tile number
    right  -- right tile number
    top    -- top tile number
    bottom -- bottom tile number
    zoom   -- map scale (0-18)
    output -- output file name default mosaic

    """
    left = int(left)
    right = int(right)
    top = int(top)
    bottom = int(bottom)
    zoom = int(zoom)
    assert(right>=left)
    assert(bottom>=top)

    filename = getname(output, maptype)
    download(left, right, top, bottom, zoom, filename, maptype)
    _mosaic(left, right, top, bottom, zoom, output, filename)


def download(left, right, top, bottom, zoom, filename, maptype="default"):

    for x in trange(left, right + 1):
        for y in trange(top, bottom + 1):
            path = './tiles/%s/%i/%i/%i.png' % (filename, zoom, x, y)
            if not os.path.exists(path):
                _download(x, y, zoom,filename,maptype)


def _download(x, y, z, filename, maptype):
    url = URL.get(maptype, maptype)
    path = './tiles/%s/%i/%i' % (filename, z, x) 
    map_url = url.format(x=x, y=y, z=z)
    r = requests.get(map_url)
    
    if not os.path.isdir(path):
        os.makedirs(path)
    with open('%s/%i.png' % (path, y), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()


def _mosaic(left, right, top, bottom, zoom, output, filename):

    size_x = (right - left + 1) * 256
    size_y = (bottom - top + 1) * 256
    output_im = Image.new("RGBA", (size_x, size_y))

    for x in trange(left, right + 1):
        for y in trange(top, bottom + 1):
            path = './tiles/%s/%i/%i/%i.png' % (filename, zoom, x, y)
            if os.path.exists(path):
                target_im = Image.open(path)
                # if target_im.mode == 'P':
                output_im.paste(target_im, (256 * (x - left), 256 * (y - top)))
                target_im.close()
    output = "output/"+output+".png"
    output_path = os.path.split(output)
    if len(output_path) > 1 and len(output_path) != 0:
        if not os.path.isdir(output_path[0]):
            os.makedirs(output_path[0])
    output_im.save(output)
    output_im.close()


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

def getname(output,maptype):
    url = URL.get(maptype, maptype)
    return maptype if url != maptype else output


def config():
    cf = configparser.ConfigParser()
    cf.read("config.conf", encoding="utf-8-sig")
    download = cf.get("config","下载方式")
    left = cf.get("config","左上横轴")
    top = cf.get("config","左上纵轴")
    right = cf.get("config","右下横轴")
    bottom = cf.get("config","右下纵轴")
    zoom = cf.get("config","级别")
    name = cf.get("config","项目名")
    maptype = cf.get("config","地图地址")

    if download == "瓦片编码":
        process_tilenum(left,right,top,bottom,zoom,name,maptype)
    elif download == "地理编码":
        process_latlng(top,left,bottom,right,zoom,name,maptype)



def test():
    process_tilenum(803,857,984,1061,8,'WORKNET')


def cml():
    if not len(sys.argv) in [7, 8]:
        print('input 7 parameter northeast latitude,northeast longitude, southeast latitude, southeast longitude,zoom , output file, map type like gaode')
        return
    process_latlng(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), str(sys.argv[6]), str(sys.argv[7]))

if __name__ == '__main__':
    config()
    # test()
    # cml()
