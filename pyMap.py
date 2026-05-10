"""
github: https://github.com/brandonxiang/pyMap
license: MIT
"""
import os
import sys
import math
import argparse
import configparser
from typing import Dict, List, Optional, Tuple, Union

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


def config(config_file: str = "config.conf") -> None:
    """Read a config file and run the configured download mode."""
    cf = configparser.ConfigParser()
    cf.read(config_file, encoding="utf-8-sig")
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
    """Backward-compatible wrapper for the historical command-line helper."""
    main(sys.argv[1:])


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    """Attach output and map source options shared by download commands."""
    parser.add_argument(
        "-o",
        "--output",
        default="mosaic",
        help="Output name; the final image is saved as output/<name>.png.",
    )
    parser.add_argument(
        "-m",
        "--maptype",
        default="default",
        help="Built-in map source key or custom URL template.",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the public command-line parser."""
    parser = argparse.ArgumentParser(
        prog="pymap",
        description="Download raster map tiles and stitch them into a PNG mosaic.",
    )
    subparsers = parser.add_subparsers(dest="command")

    latlng_parser = subparsers.add_parser(
        "latlng",
        help="Download by geographic bounds.",
    )
    latlng_parser.add_argument("north", type=float, help="North latitude.")
    latlng_parser.add_argument("west", type=float, help="West longitude.")
    latlng_parser.add_argument("south", type=float, help="South latitude.")
    latlng_parser.add_argument("east", type=float, help="East longitude.")
    latlng_parser.add_argument("zoom", type=int, help="Web Mercator zoom level.")
    _add_common_options(latlng_parser)

    tilenum_parser = subparsers.add_parser(
        "tilenum",
        help="Download by inclusive tile-number bounds.",
    )
    tilenum_parser.add_argument("left", type=int, help="Left tile x number.")
    tilenum_parser.add_argument("right", type=int, help="Right tile x number.")
    tilenum_parser.add_argument("top", type=int, help="Top tile y number.")
    tilenum_parser.add_argument("bottom", type=int, help="Bottom tile y number.")
    tilenum_parser.add_argument("zoom", type=int, help="Web Mercator zoom level.")
    _add_common_options(tilenum_parser)

    config_parser = subparsers.add_parser(
        "config",
        help="Run a download from a Chinese config file.",
    )
    config_parser.add_argument(
        "-f",
        "--file",
        default="config.conf",
        help="Config file path. Defaults to config.conf.",
    )

    subparsers.add_parser("sources", help="List built-in map source keys.")
    return parser


def _run_legacy_latlng(argv: List[str]) -> int:
    """Run the historical seven-argument geographic-bounds command."""
    process_latlng(
        float(argv[0]),
        float(argv[1]),
        float(argv[2]),
        float(argv[3]),
        int(argv[4]),
        str(argv[5]),
        str(argv[6]),
    )
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Run the ``pymap`` command-line interface."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        config()
        return 0

    # Keep existing third-party invocations working:
    # python pyMap.py north west south east zoom output maptype
    if len(argv) == 7 and argv[0] not in {"latlng", "tilenum", "config", "sources"}:
        return _run_legacy_latlng(argv)

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "latlng":
        process_latlng(
            args.north,
            args.west,
            args.south,
            args.east,
            args.zoom,
            args.output,
            args.maptype,
        )
        return 0
    if args.command == "tilenum":
        process_tilenum(
            args.left,
            args.right,
            args.top,
            args.bottom,
            args.zoom,
            args.output,
            args.maptype,
        )
        return 0
    if args.command == "config":
        config(args.file)
        return 0
    if args.command == "sources":
        for name in sorted(URL):
            print(name)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
