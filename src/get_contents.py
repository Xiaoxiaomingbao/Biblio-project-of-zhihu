# 本程序文件用于从contents.html文件中获取知乎电子书的目录，包括篇章名、篇章等级、链接，使用二重列表依次存储
# 主要针对知乎电子书，其他类型的网页版电子书我还没想好
import re


# 与之前的tag_pair函数不同，本函数用于从给定字符串中找出全部带属性的标签对，返回包括标签对的字符串
def new_tag_pair(string,tag):
    tag_start = '<' + tag
    tag_end = '</' + tag + '>'
    tags = []
    for i in range(len(string) - len(tag_start)):
        if string[i:i + len(tag_start)] == tag_start:
            for j in range(i + len(tag_start),len(string) - len(tag_end)):
                if string[j:j + len(tag_end)] == tag_end:
                    break
            tags.append(string[i:j + len(tag_end)])
    return tags


def new_new_tag_pair(string,tag):
    tag_start = '<' + tag
    tag_end = tag_start
    tags = []
    for i in range(len(string) - len(tag_start)):
        if string[i:i + len(tag_start)] == tag_start:
            for j in range(i + len(tag_start),len(string) - len(tag_end)):
                if string[j:j + len(tag_end)] == tag_end:
                    break
            tags.append(string[i:j])
    return tags


def get_contents_list(html):
    contents_list = []
    # 两种类型 class=level-1 class="level-1 is-current"
    pat_li_class = re.compile(r'<li[^>]+?class\s*?=\s*?[\'"]*?([\w-]+)[\'"]*?[^>]*?>')
    pat_a_href = re.compile(r'<a[^>]+?href\s*?=\s*?[\'"]*?([^>]+)[\'"]*?>')
    pat_span_string = re.compile(r'>([^<]+)<')
    # 一般来说是第二个ul标签
    ul = new_tag_pair(html,'ul')[1]
    # HTML文件往往不规范，以至于li标签未能配对，不得不再写一个新的函数
    lis = new_new_tag_pair(ul,'li')
    for li in lis:
        content_list = []
        match = pat_li_class.search(li)
        chapter_level = match.group(1)
        a = new_tag_pair(li,'a')[0]
        match = pat_a_href.search(a)
        chapter_url = match.group(1)
        span = new_tag_pair(a,'span')[0]
        match = pat_span_string.search(span)
        chapter_name = match.group(1)
        content_list.append(chapter_name)
        content_list.append(chapter_level)
        content_list.append(chapter_url)
        contents_list.append(content_list)
        print(content_list)
    return contents_list
