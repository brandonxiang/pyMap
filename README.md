# pyMap
Raster Map Download Helper

这是一个简单的实例，去实现地图下载工具。如今又很多瓦片的下载工具，但是都是收费的，感觉既然是盗版还要收费，非常不好。我决定做一个简单的地图下载器，将瓦片下载拼接成对应的图片。

经供参考，不要从事商业用途，后果自负。

##依赖

- python3.5
- requests
- pillow

##用法

```
python pyMap.py 22.456671 113.889962 22.345576 114.212686 13 output/sample.png
```
- 参数1： 西北角纬度
- 参数2： 西北角经度
- 参数3： 东南角纬度
- 参数4： 东南角经度
- 参数5： 比例尺级别
- 参数6： 输出路径（默认'output/mosaic.png'）

##license

[MIT](LICENSE)
