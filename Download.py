from xml.dom.minidom import parse
from data_downloader import downloader

netrc = downloader.Netrc()
netrc.add('scihub.copernicus.eu', 'liury', 'liuruiyan1998', overwrite=True)

# 数据保存目录
folder_out = r'D:\js\map'
# 包含url的 products.meta4 文件（购物车数据清单）
url_file = r'D:\js\products.meta4'

data = parse(url_file).documentElement
urls = [i.childNodes[0].nodeValue for i in data.getElementsByTagName('url')]

downloader.download_datas(urls, folder_out)


