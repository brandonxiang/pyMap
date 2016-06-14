# pyMap
Raster Map Download Helper

这是一个简单的实例，去实现地图下载工具。如今又很多瓦片的下载工具，但是都是收费的，感觉既然是盗版还要收费，非常不好。我决定做一个简单的地图下载器，将瓦片下载拼接成对应的图片。

经供参考，不要从事商业用途，后果自负。

##依赖

- python3.5
- requests 负责下载功能
- pillow 负责图片拼接
- tqdm 负责进度条

##安装

1. 安装python3.5

2. 安装对应的第三方库

```
pip install -r requirement.txt
```

##用法

###运用命令行

```
python pyMap.py 22.456671 113.889962 22.345576 114.212686 13 output/sample.png
```

- 参数1： 西北角纬度
- 参数2： 西北角经度
- 参数3： 东南角纬度
- 参数4： 东南角经度
- 参数5： 比例尺级别
- 参数6： 输出路径（默认'output/mosaic.png'）

###hard code test function

请自修修改，下面是通过经纬度下载数据。

```
def test():
    process_latlng(22.4566710000, 113.8899620000, 22.3455760000, 114.2126860000, 13)
```

或者通过瓦片编号下载数据。

```
def test():
    process_tilenum(1566, 1788, 1976, 2149, 9, "output/overlay.png")
```

##license

[MIT](LICENSE)
