import re
import cssutils
from pythonds.basic import Stack


class SubstringNotFoundError(Exception):
    """自定义异常：找不到指定的子串"""

    def __init__(self, substring):
        super().__init__(f"Element '{substring}' not found.")
        self.sub = substring


def tag_pair(text, tag_name, order):
    """获取不带属性的标签对之间的字符串，不含标签对本身，找不到则抛出SubstringNotFoundError异常。
    order为假，只找第一对标签；order为真，找出所有标签对。只取style标签的内容中.ZhihuEPub后方的{}内样式设置。"""
    if order:
        returned = ''
        while 1:
            try:
                temp = tag_pair(text, tag_name, 1)
                returned = returned + select_css(temp)
            except SubstringNotFoundError:
                break
        return returned

    if not hasattr(tag_pair, 'saved'):
        tag_pair.saved = 0
    st = '<' + tag_name + '>'
    nd = '</' + tag_name + '>'
    start = None
    end = None
    for i in range(tag_pair.saved, len(text)):
        if text[i:i + len(st)] == st:
            start = i + len(st)
            break
    if start is None:
        raise SubstringNotFoundError(st)
    for i in range(start, len(text)):
        if text[i:i + len(nd)] == nd:
            end = i - 1
            break
    if end is None:
        raise SubstringNotFoundError(nd)
    tag_pair.saved = end
    return text[start:end + 1]


def select_css(style):
    start = 0
    selected_css = ''
    while 1:
        try:
            start = style.index('.ZhihuEPub', start, len(style) - 1)
            try:
                end = style.index('}', start, len(style) - 1)
                selected_css = selected_css + style[start: end + 1]
                start = end
            except ValueError:
                print('找不到“}”')
        except ValueError:
            break
    return selected_css


def get_selector_text(selector):
    """从selector对象中获得属性selectorText的属性值"""
    select = str(selector)
    pat_selector = re.compile(r'selectorText=\'(.+)\'', flags=0)
    match = pat_selector.search(select)
    return match.group(1)


def get_css_class(css):
    """获得CSS中全部选择器所涉及的类，返回集合，注意其中的类名带“.”"""
    css_class = set()
    # 创建CSS解析器
    parser = cssutils.CSSParser()
    # 解析CSS代码
    sheet = parser.parseString(css)
    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            selectors = rule.selectorList
            pat = re.compile(r'\.[\w-]+')
            for selector in selectors:
                selector = get_selector_text(selector)
                css_class.update(pat.findall(selector))
    return css_class


def get_block_classes(block):
    """获得正文部分全部标签的类属性，返回集合"""
    classes = set()
    pat_tag_st = re.compile(r'<[^/][^>]*?>')
    for match in pat_tag_st.finditer(block):
        tag_class = get_tag_class(match.group(0))
        classes.add(tag_class)
    return classes


def verify_class(slc, classes):
    pat_css_class = re.compile(r'\.([\w-]+)', flags=0)
    # 因为难以获取css中的标签名，就只好这样了
    if 'button' in slc or 'Button' in slc:
        start = False
    else:
        start = True
    for match in pat_css_class.finditer(slc):
        if classes:
            start = start and (match.group(1) in classes)
    return start


def rule_process(rule, classes):
    i = 0
    new_selectors_text = ''
    for selector in rule.selectorList:
        # 万万不可直接类型强转
        slc = get_selector_text(selector)
        if verify_class(slc, classes):
            if not i:
                new_selectors_text = new_selectors_text + slc
            else:
                new_selectors_text = new_selectors_text + ', ' + slc
        i = i + 1
    if new_selectors_text:
        new_rule = cssutils.css.CSSStyleRule(selectorText=new_selectors_text)
        new_rule.style.cssText = rule.style.cssText
        return new_rule
    else:
        # 此情况下整条规则都要删除
        return ''


def modify_css(css, classes):
    # 创建一个新的 CSSStyleSheet 对象
    new_sheet = cssutils.css.CSSStyleSheet()
    # 创建CSS解析器
    parser = cssutils.CSSParser()
    # 解析CSS代码
    sheet = parser.parseString(css)

    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            new_rule = rule_process(rule, classes)
            if new_rule:
                new_sheet.insertRule(new_rule)

    # 将样式表输出为 CSS 文本
    new_sheet_text = new_sheet.cssText.decode('utf-8')
    return new_sheet_text


def get_tag_class(tag):
    """获取标签前半部分中的类属性（默认只有一个类属性，且属性值中无空格）"""
    pat_class = re.compile(r'class\s*?=\s*?[\'"]*?([\w-]+)[\'"]*?')
    try:
        match = pat_class.search(tag)
        return match.group(1)
    except AttributeError:
        # 捕获在调用 match.group(1) 时引发的异常
        return ''
    except re.error:
        # 捕获正则表达式错误
        return ''


def modify_span(html, classes):
    """输入正文部分的HTML代码，根据有用的CSS的类属性去除span标签的无用成分"""
    new_html = ''

    # 先遍历span标签，要考虑到span标签除类属性外还可能有其他属性，类属性无用只删类属性
    pat_span_st = re.compile(r'<span[^>]*?>')
    pat_span_nd = re.compile(r'</span[^>]*?>')
    span_st = []
    span_nd = []

    for match in pat_span_st.finditer(html):
        span_st.append(match.span())

    for match in pat_span_nd.finditer(html):
        span_nd.append(match.span())

    i = 0
    j = 0
    k = 0
    spans = Stack()
    while True:
        if i >= len(html) - 1:
            break
        elif i == span_st[j][0]:
            span_start = html[span_st[j][0]:span_st[j][1]]
            span_class = get_tag_class(span_start)
            if '.' + span_class in classes:
                spans.push(True)
                new_html = new_html + span_start
            else:
                spans.push(False)
            i = span_st[j][1]
            if j < len(span_st) - 1:
                j = j + 1
        elif i == span_nd[k][0]:
            span_check = spans.pop()
            if span_check:
                new_html = new_html + html[span_nd[k][0]:span_nd[k][1]]
            i = span_nd[k][1]
            if k < len(span_nd) - 1:
                k = k + 1
        else:
            new_html = new_html + html[i]
            i = i + 1
    return new_html


def refine(html):
    """精简HTML文本，去除无用成分"""
    try:
        title = tag_pair(html, 'title', 0)
    except SubstringNotFoundError:
        print('title为空')
        title = ''

    try:
        css = tag_pair(html, 'style', 1)
    except SubstringNotFoundError:
        print('css为空')
        css = ''

    try:
        block = tag_pair(html, 'section', 0)
    except SubstringNotFoundError:
        print('block为空')
        block = ''

    # 提取HTML文件的第一条注释（关于SingleFile下载的信息）
    pat_note = re.compile(r'<!-{2,}[^!]*?-{2,}>')
    match = pat_note.search(html)
    note = match.group(0)
    pat_note_url = re.compile(r'url:\s*?(\S+)\s*?')
    match = pat_note_url.search(note)
    note_url = match.group(1)
    print('HTML文件的URL为：' + note_url)

    # 处理span标签
    useful_class = get_css_class(css)
    block = modify_span(block, useful_class)
    # 处理img标签

    new_html = ''.join([
        '<?xml version="1.0" encoding="utf-8"?> ',
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"> ',
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN"> ',
        note,
        '<head> <title> ',
        title,
        '</title> <style> ',
        css,
        '</style> </head> <body> <div> ',
        block,
        '</div> </body> </html> '
    ])

    refined_dict = {note_url: new_html}
    return refined_dict
