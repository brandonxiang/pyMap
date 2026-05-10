"""
github: https://github.com/brandonxiang/pyMap
license: MIT
"""
import os
import sys
import math
import configparser
from typing import Dict, Tuple, Union

import requests
from PIL import Image
from tqdm import trange

Number = Union[int, float, str]


URL = {  # type: Dict[str, str]
    "gaode": "http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}",
    "gaode.image": "http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
    "tianditu": "http://t2.tianditu.cn/DataServer?T=vec_w&X={x}&Y={y}&L={z}",
    "googlesat": "http://khm0.googleapis.com/kh?v=203&hl=zh-CN&&x={x}&y={y}&z={z}",
    "tianditusat":"http://t2.tianditu.gov.cn/DataServer?T=img_w&X={x}&Y={y}&L={z}&tk=your takon key",
    "tianditu.road":"http://t2.tianditu.gov.cn/DataServer?T=cia_w&X={x}&Y={y}&L={z}&tk=your takon key",
    "esrisat":"http://server.arcgisonline.com/arcgis/rest/services/world_imagery/mapserver/tile/{z}/{y}/{x}",
    "gaode.road": "http://webst02.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scale=1&style=8",
    "default":"http://61.144.226.124:9001/map/GISDATA/WORKNET/{z}/{y}/{x}.png",
    "szbuilding":"http://61.144.226.124:9001/map/GISDATA/SZBUILDING/{z}/{y}/{x}.png",
    "szbase":"http://61.144.226.44:6080/arcgis/rest/services/basemap/szmap_basemap_201507_01/MapServer/tile/{z}/{y}/{x}"
}


def process_latlng(
    north: Number,
    west: Number,
    south: Number,
    east: Number,
    zoom: Number,
    output: str = "mosaic",
    maptype: str = "default",
) -> None:
    """Download tiles for a geographic bounding box and mosaic them.

    Args:
        north: North latitude of the bounding box.
        west: West longitude of the bounding box.
        south: South latitude of the bounding box.
        east: East longitude of the bounding box.
        zoom: Web Mercator tile zoom level.
        output: Output image name without extension.
        maptype: Built-in map source key or a custom URL template.
    """
    north = float(north)
    west = float(west)
    south = float(south)
    east = float(east)
    zoom = int(zoom)
    assert(east > -180 and east < 180)
    assert(west > -180 and west < 180)
    assert(north > -90 and north < 90)
    assert(south > -90 and south < 90)
    assert(west < east)
    assert(north > south)

    # Convert the geographic box to the inclusive tile-number range used by
    # the downloader. North/west maps to the top-left tile; south/east maps to
    # the bottom-right tile.
    left, top = latlng2tilenum(north, west, zoom)
    right, bottom = latlng2tilenum(south, east, zoom)
    process_tilenum(left, right, top, bottom, zoom, output, maptype)


def process_tilenum(
    left: Number,
    right: Number,
    top: Number,
    bottom: Number,
    zoom: Number,
    output: str = "mosaic",
    maptype: str = "default",
) -> None:
    """Download tiles by tile-number bounds and mosaic them.

    Args:
        left: Left tile x number.
        right: Right tile x number.
        top: Top tile y number.
        bottom: Bottom tile y number.
        zoom: Web Mercator tile zoom level.
        output: Output image name without extension.
        maptype: Built-in map source key or a custom URL template.
    """
    left = int(left)
    right = int(right)
    top = int(top)
    bottom = int(bottom)
    zoom = int(zoom)
    assert(right >= left)
    assert(bottom >= top)

    filename = getname(output, maptype)
    download(left, right, top, bottom, zoom, filename, maptype)
    _mosaic(left, right, top, bottom, zoom, output, filename)


def download(
    left: int,
    right: int,
    top: int,
    bottom: int,
    zoom: int,
    filename: str,
    maptype: str = "default",
) -> None:
    """Download missing tile files into the local cache directory."""

    for x in trange(left, right + 1):
        for y in trange(top, bottom + 1):
            path = "./tiles/%s/%i/%i/%i.png" % (filename, zoom, x, y)
            if not os.path.exists(path):
                _download(x, y, zoom, filename, maptype)


def _download(x: int, y: int, z: int, filename: str, maptype: str) -> None:
    """Download one tile and write it as ``tiles/<name>/<z>/<x>/<y>.png``."""
    url = URL.get(maptype, maptype)
    path = "./tiles/%s/%i/%i" % (filename, z, x)
    map_url = url.format(x=x, y=y, z=z)
    r = requests.get(map_url)

    if not os.path.isdir(path):
        os.makedirs(path)

    if r.status_code != 200:
        print("request %i %i got response:%i" % (x, y, r.status_code))
    elif r.status_code == 200:
        with open("%s/%i.png" % (path, y), "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()


def _mosaic(
    left: int,
    right: int,
    top: int,
    bottom: int,
    zoom: int,
    output: str,
    filename: str,
) -> None:
    """Merge cached 256x256 tiles into a single output PNG."""

    size_x = (right - left + 1) * 256
    size_y = (bottom - top + 1) * 256
    output_im = Image.new("RGBA", (size_x, size_y))

    for x in trange(left, right + 1):
        for y in trange(top, bottom + 1):
            path = "./tiles/%s/%i/%i/%i.png" % (filename, zoom, x, y)
            if os.path.exists(path):
                target_im = Image.open(path)
                # Paste each tile at the offset relative to the top-left tile
                # of the requested tile rectangle.
                output_im.paste(target_im, (256 * (x - left), 256 * (y - top)))
                target_im.close()
    output = "output/" + output + ".png"
    output_path = os.path.split(output)
    if len(output_path) > 1 and len(output_path) != 0:
        if not os.path.isdir(output_path[0]):
            os.makedirs(output_path[0])
    output_im.save(output)
    output_im.close()


def latlng2tilenum(lat_deg: float, lng_deg: float, zoom: int) -> Tuple[int, int]:
    """Convert latitude/longitude into Web Mercator tile coordinates.

    Args:
        lat_deg: Latitude in degrees.
        lng_deg: Longitude in degrees.
        zoom: Web Mercator tile zoom level.

    Returns:
        A tuple of ``(x_tile, y_tile)`` numbers.
    """
    n = math.pow(2, int(zoom))
    xtile = ((lng_deg + 180) / 360) * n
    lat_rad = lat_deg / 180 * math.pi
    ytile = (1 - (math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi)) / 2 * n
    return math.floor(xtile), math.floor(ytile)


def getname(output: str, maptype: str) -> str:
    """Return the cache directory name for a map source."""
    url = URL.get(maptype, maptype)
    return maptype if url != maptype else output


def config() -> None:
    """Read ``config.conf`` and run the configured download mode."""
    cf = configparser.ConfigParser()
    cf.read("config.conf", encoding="utf-8-sig")
    download_type = cf.get("config", "下载方式")
    left = cf.get("config", "左上横轴")
    top = cf.get("config", "左上纵轴")
    right = cf.get("config", "右下横轴")
    bottom = cf.get("config", "右下纵轴")
    zoom = cf.get("config", "级别")
    name = cf.get("config", "项目名")
    maptype = cf.get("config", "地图地址")

    if download_type == "瓦片编码":
        process_tilenum(left, right, top, bottom, zoom, name, maptype)
    elif download_type == "地理编码":
        process_latlng(top, left, bottom, right, zoom, name, maptype)


def test() -> None:
    """Run the historical hard-coded sample download."""
    process_tilenum(803, 857, 984, 1061, 8, "WORKNET")


def cml() -> None:
    """Parse CLI arguments and run a geographic-bounds download."""
    if not len(sys.argv) in [7, 8]:
        print(
            "input 7 parameter northeast latitude,northeast longitude, "
            "southeast latitude, southeast longitude,zoom , output file, "
            "map type like gaode"
        )
        return
    process_latlng(
        float(sys.argv[1]),
        float(sys.argv[2]),
        float(sys.argv[3]),
        float(sys.argv[4]),
        int(sys.argv[5]),
        str(sys.argv[6]),
        str(sys.argv[7]),
    )


if __name__ == "__main__":
    config()
    # test()
    # cml()
