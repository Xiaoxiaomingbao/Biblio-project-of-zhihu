# 注意：该文件是程序第二部分的入口
# 重申：程序的目标是制作epub2.0文件
import os
from datetime import datetime
import shutil
from set_ncx import set_the_ncx


def put_metadata(key):
    if key == 'contributor':
        value = 'Biblio Project, with the help of SingleFile(Google Chrome extension)'
    elif key == 'time':
        value = str(datetime.now())
    else:
        prompt = '输入' + key
        value = input(prompt)
    dc = 'dc:' + key
    return '<' + dc + '>' + value + '</' + dc + '>'


def split_filename(filename):
    for i in range(len(filename) - 1,0,-1):
        if filename[i] == '.':
            break
    parts = []
    parts.append(filename[:i])
    parts.append(filename[i + 1:])
    return parts


book_name = input('输入书所在的文件夹的路径')
contents_path = os.path.join(book_name,'contents.txt')
Text_path = os.path.join(book_name,'OEBPS','Text')
Images_path = os.path.join(book_name,'OEBPS','Images')

with open(contents_path,'r',encoding='UTF-8') as f:
    contents_list = f.read()
contents_list = eval(contents_list)

# 关于id的规定：toc.ncx的id设置为ncx，图片的id设置为除去扩展名的文件名，HTML的id设置为section加四位编号    image0001.png    0001 封面.html

# 设置package大标签
opf = '''
<?xml version="1.0" encoding="utf-8"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf">
'''

# metadata标签
metadata = '<metadata xmlns:opf="http://www.idpf.org/2007/opf">'
metadata = metadata + put_metadata('title')
# metadata = metadata + put_metadata('creator')
# metadata = metadata + put_metadata('publisher')
# metadata = metadata + put_metadata('time')
# metadata = metadata + put_metadata('language')
# metadata = metadata + put_metadata('contributor')
metadata = metadata + '</metadata>'
opf = opf + metadata

# manifest标签
manifest = '<manifest>'
item = '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
manifest = manifest + item
part1 = '<item id="'
part2 = '" href="'
part3 = '" media-type="'
part4 = '"/>'
ids = []

for p in os.listdir(Text_path):
    folder,filename = os.path.split(p)
    item_id = 'section' + filename[4:8]
    ids.append(item_id)
    item = part1 + item_id + part2 + 'Text/' + filename + part3 + 'application/xhtml+xml' + part4
    manifest = manifest + item

for p in os.listdir(Images_path):
    folder,filename = os.path.split(p)
    item_id,filetype = split_filename(filename)
    item = part1 + item_id + part2 + 'Images/' + filename + part3 + 'image/' + filetype + part4
    manifest = manifest + item

manifest = manifest + '</manifest>'
opf = opf + manifest

# spine标签
spine = '<spine toc="ncx">'
part1 = '<itemref idref="'
part2 = '"/>'
ids = sorted(ids)
for item_id in ids:
    item = part1 + item_id + part2
    spine = spine + item
spine = spine + '</spine>'
opf = opf + spine

# guide标签
cover_path = input('输入封面路径，相对于opf文件')
guide = '<guide><reference type="cover" title="封面" href="'
guide = guide + cover_path
guide = guide + '"/>' + '</guide>'
opf = opf + guide


opf = opf + '</package>'
opf_path = os.path.join(book_name,'OEBPS','content.opf')
with open(opf_path,'w',encoding='UTF-8') as f:
    f.write(opf)

# 调用另一程序文件
set_the_ncx(contents_list,book_name)

# 复制两个固定文件
container_path = os.path.join(book_name,'META-INF')
os.mkdir(container_path)
shutil.copy('../res/container.xml', container_path)
shutil.copy('../res/mimetype', book_name)
