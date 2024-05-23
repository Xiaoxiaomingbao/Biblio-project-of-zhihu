from src.get_contents import get_contents_list
from src.HTML_refine import refine
from src.image_arrange import *

# 获取电子书的书名（文件夹名）
book_name = input('输入书所在的文件夹的路径')

# 重整电子书文件夹
OEBPS_path = os.path.join(book_name, 'OEBPS')
os.mkdir(OEBPS_path)
Text_path = os.path.join(OEBPS_path, 'Text')
os.mkdir(Text_path)
Images_path = os.path.join(OEBPS_path, 'Images')
os.mkdir(Images_path)

# 这里要求电子书文件夹中必须有contents.html
contents_path = os.path.join(book_name, 'contents.html')
with open(contents_path, 'r', encoding='UTF-8') as f:
    contents_html = f.read()
contents_list = get_contents_list(contents_html)
# 删除多余的contents.html
os.remove(contents_path)
# 将contents写入文件夹内的txt中
contents_path = os.path.join(book_name, 'contents.txt')
with open(contents_path, 'w', encoding='UTF-8') as f:
    for content in contents_list:
        f.write(str(content) + '\n')
print('完成目录获取！')

# 对HTML文件进行除冗
for f in os.listdir(book_name):
    if f.endswith('.html'):
        f_path = os.path.join(book_name, f)
        with open(f_path, 'r', encoding='UTF-8') as ff:
            html_content = ff.read()
        dictionary = refine(html_content)
        urls = dictionary.keys()
        urls = list(urls)
        url = urls[0]
        new_html_content = dictionary[url]
        # 创建新的文件名new_f
        new_f = None
        for i in range(len(contents_list)):
            content_list = contents_list[i]
            if url == content_list[2]:
                # new_f = format_num(i + 1) + ' ' + content_list[0] + '.html'
                new_f = 'part' + format_num(i + 1) + '.html'
                break
        # 使用新的文件名
        assert new_f is not None
        new_f_path = os.path.join(Text_path, new_f)
        os.rename(f_path, new_f_path)
        with open(new_f_path, 'w', encoding='UTF-8') as ff:
            ff.write(new_html_content)
        print('完成除冗：' + new_f)


# 封面可能有对应的HTML，也可能没有；若没有，封面的图片在命名上不遵循其他图片的命名规范
# 处理电子书HTML中的图片
# 用来标记图片的序号，序号从1开始
accu = 0
htmls = [os.path.join(Text_path, f) for f in os.listdir(Text_path) if f.endswith('.html')]
htmls = sorted(htmls)
for f in htmls:
    print('准备提取图片 来自' + f)
    accu = arrange(f, Images_path, accu)
