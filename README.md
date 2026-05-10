# 🗺️ pyMap

**A lightweight Python helper for downloading raster map tiles and stitching them into a single image.**

`pyMap` converts a geographic bounding box or an explicit tile range into Web Mercator tile coordinates, downloads missing tiles into a local cache, and mosaics the cached tiles into a PNG output.

## ✨ Highlights

- 🧭 **Two download modes**: geographic coordinates or tile numbers.
- 🧩 **Tile mosaic output**: merges 256x256 tiles into one PNG image.
- 💾 **Local tile cache**: skips tiles that already exist under `tiles/`.
- 🗺️ **Built-in map sources**: Gaode, Tianditu, Google satellite, Esri satellite, and custom URL templates.
- 🧪 **Unit-tested core flow**: coordinate conversion, validation, download dispatch, cache skip, and file writing.
- 📝 **Typed and documented code**: core functions include Python type hints and docstrings.

## ⚠️ Usage Notice

This project is intended for learning, research, and personal tooling. Please respect map provider terms of service, copyright, rate limits, and local laws. Do not use it for unauthorized commercial map downloads.

## 📦 Requirements

- Python 3.5+
- `requests` for HTTP downloads
- `Pillow` for image composition
- `tqdm` for progress output

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

Run with a geographic bounding box:

```bash
python pyMap.py 22.456671 113.889962 22.345576 114.212686 13 sample gaode
```

Arguments:

| #   | Name        | Description                                      |
| --- | ----------- | ------------------------------------------------ |
| 1   | north       | Northwest latitude                               |
| 2   | west        | Northwest longitude                              |
| 3   | south       | Southeast latitude                               |
| 4   | east        | Southeast longitude                              |
| 5   | zoom        | Web Mercator tile zoom level                     |
| 6   | output      | Output image name; saved as `output/<name>.png`  |
| 7   | map type    | Built-in source key or custom tile URL template  |

## ⚙️ Configuration File

`pyMap.py` reads `config.conf` when run directly.

### Tile-number mode

```ini
[config]
下载方式 = 瓦片编码
左上横轴 = 803
左上纵轴 = 984
右下横轴 = 857
右下纵轴 = 1061
级别 = 8
项目名 = test
地图地址 = default
```

### Geographic-coordinate mode

```ini
[config]
下载方式 = 地理编码
左上横轴 = 113.889962
左上纵轴 = 22.456671
右下横轴 = 114.212686
右下纵轴 = 22.345576
级别 = 13
项目名 = sample
地图地址 = gaode
```

## 🧑‍💻 Programmatic Usage

Download by geographic coordinates:

```python
from pyMap import process_latlng

process_latlng(
    north=22.456671,
    west=113.889962,
    south=22.345576,
    east=114.212686,
    zoom=13,
    output="sample",
    maptype="gaode",
)
```

Download by tile numbers:

```python
from pyMap import process_tilenum

process_tilenum(
    left=1566,
    right=1788,
    top=1976,
    bottom=2149,
    zoom=9,
    output="overlay",
    maptype="default",
)
```

## 🗺️ Map Sources

Built-in source keys are defined in `pyMap.py`:

- `gaode`
- `gaode.image`
- `gaode.road`
- `tianditu`
- `tianditusat`
- `tianditu.road`
- `googlesat`
- `esrisat`
- `default`
- `szbuilding`
- `szbase`

You can also pass a custom URL template with `{x}`, `{y}`, and `{z}` placeholders:

```python
process_tilenum(
    1,
    2,
    3,
    4,
    5,
    output="custom",
    maptype="https://example.com/tiles/{z}/{x}/{y}.png",
)
```

## 📁 Output Layout

```text
tiles/<cache-name>/<zoom>/<x>/<y>.png
output/<output-name>.png
```

For built-in map sources, `<cache-name>` is the source key. For custom URL templates, `<cache-name>` is the `output` value.

## 🧪 Testing

Run the standard-library test suite:

```bash
python3 -m unittest discover -s tests -v
```

If `pytest` is available, the suite also works through:

```bash
pytest
```

## 🧭 Related Projects

- [brandonxiang/pyMap](https://github.com/brandonxiang/pyMap) - Raster map download helper in Python.
- [brandonxiang/pyMap_GFW](https://github.com/brandonxiang/pyMap_GFW) - Selenium/PhantomJS-based raster map helper.
- [brandonxiang/pyMap_webapp](https://github.com/brandonxiang/pyMap_webapp) - Web app version of pyMap.
- [brandonxiang/nodemap_spider](https://github.com/brandonxiang/nodemap_spider) - Electron crawler for raster maps.
- [brandonxiang/nodemap](https://github.com/brandonxiang/nodemap) - Electron app for nodemap_spider.

## 📄 License

[MIT](LICENSE)
