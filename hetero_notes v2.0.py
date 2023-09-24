# 本程序用于处理大量篇章的注释内容集中于某处的情形，这里的某处应解释为某个HTML文件的末尾
# a标签的原href的头部必须为https://www.zhihu.com/pub/reader，否则直接忽略
# 请人为检查匹配到的a标签总数是否为偶数！

import os
import re

book_name = input('输入电子书文件夹路径')
Text_path = os.path.join(book_name,'OEBPS','Text')


# 从start_num的下一个开始标号
def set_quote(file_name,span,start_num,quote_file):
    global Text_path
    file_path = os.path.join(Text_path,file_name)
    with open(file_path,'r') as f:
        file_html = f.read()
    new_html = ''
    end = 0
    for i in range(len(span)):
        start = span[i][0]
        print('生成quote' + str(start_num + i + 1))
        quote = '<a class=footnote_quote' + ' id=footnote_quote_' + str(start_num + i + 1) + ' href=' + quote_file[0] + '#footnote_content_' + str(start_num + i + 1) + ' >'
        quote_file.append(file_name)
        new_html = new_html + file_html[end:start] + quote
        end = span[i][1]
    start = len(file_html)
    new_html = new_html + file_html[end:start]
    with open(file_path,'w') as f:
        f.write(new_html)


def quote_content(file_name,span,num,start_num,quote_file):
    global Text_path
    file_path = os.path.join(Text_path,file_name)
    with open(file_path,'r') as f:
        file_html = f.read()
    new_html = ''
    end = 0
    for i in range(len(span)):
        start = span[i][0]
        if i + 1 > num:
            print('生成content' + str(i + 1 - num))
            note = '<a class=footnote_content' + ' id=footnote_content_' + str(i + 1 - num) + ' href=' + quote_file[i + 1 - num] + '#footnote_quote_' + str(i + 1 - num) + ' >'
        else:
            print('生成quote' + str(start_num + i + 1))
            note = '<a class=footnote_quote' + ' id=footnote_quote_' + str(start_num + i + 1) + ' href=' +  quote_file[0] + '#footnote_content_' + str(start_num + i + 1) + ' >'
            quote_file.append(file_name)
        new_html = new_html + file_html[end:start] + note
        end = span[i][1]
    start = len(file_html)
    new_html = new_html + file_html[end:start]
    with open(file_path,'w') as f:
        f.write(new_html)


# 默认结束的文件集中了注释的内容
file_names = os.listdir(Text_path)
file_names = sorted(file_names)
start = int(input('开始的文件名序号（包含）'))
end = int(input('结束的文件名序号（包含）'))
file_names = file_names[(start - 1):end]

pat = re.compile(r'<a[^>]+>')

spans = []
total = 0
for file_name in file_names:
    file_path = os.path.join(Text_path,file_name)
    span = []
    with open(file_path,'r') as f:
        file_html = f.read()
    for match in pat.finditer(file_html):
        if 'https://www.zhihu.com/pub/reader' in match.group(0):
            span.append(match.span(0))
    print(file_name + ' ' + str(len(span)))
    total = total + len(span)
    spans.append(span)
print('总计' + ' ' + str(total))

order = int(input('输入0继续'))
if order:
    exit(0)

half = total // 2
accu = 0
quote_file = [file_names[-1]]
for i in range(len(file_names)):
    file_name = file_names[i]
    if file_name == file_names[-1]:
        print('调用quote_content')
        quote_content(file_name,spans[i],len(spans[i]) - half,accu,quote_file)
    else:
        print('调用set_quote')
        set_quote(file_name,spans[i],accu,quote_file)
        accu = accu + len(spans[i])
