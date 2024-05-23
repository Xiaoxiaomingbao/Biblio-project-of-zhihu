import re
import cssutils
from pythonds.basic import Stack


class SubstringNotFoundError(Exception):
    """自定义异常：找不到指定的子串"""
    def __init__(self, substring):
        super().__init__(f"Element '{substring}' not found.")
        self.sub = substring


def tag_pair(text, tag_name, order):
    """用来获取一对不带属性的标签间的字符串，只找出现的第一对标签，order为真则返回的字符串不含两侧标签"""
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
    if order:
        return text[start:end + 1]
    else:
        return text[start - len(st):end + len(nd) + 1]


def get_selector_text(selector):
    select = str(selector)
    pat_selector = re.compile(r'selectorText=\'(.+)\'', flags=0)
    match = pat_selector.search(select)
    return match.group(1)


def get_css_class(css):
    css_class = set()
    # 创建CSS解析器
    parser = cssutils.CSSParser()
    # 解析CSS代码
    sheet = parser.parseString(css)
    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            selectors = rule.selectorList
            pat1 = re.compile(r'\.[\w-]+')
            for selector in selectors:
                selector = get_selector_text(selector)
                css_class.update(pat1.findall(selector))
    # 注意这里的class名带“.”
    return css_class


def get_block_classes(block):
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
    # 只针对标签（前半部分），默认只有一个class属性
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
    new_html = ''

    # 先遍历span标签，这里只考虑span的class属性
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
    # 提取出CSS和所需块元素的文本字符串，当然还有一些其他内容
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

    classes = get_block_classes(block)
    css_refined = modify_css(css, classes)
    # 注意new_classes的每个元素前都带“.”
    new_classes = get_css_class(css_refined)
    # 为了防止由于block内不含span标签（如封面）而引发的异常
    try:
        block_refined = modify_span(block, new_classes)
    except SubstringNotFoundError:
        block_refined = block

    new_html = ''.join([
        '<!DOCTYPE html> <html lang=zh> ',
        note,
        '<head> <meta charset=utf-8> ',
        title,
        '<style> ',
        css_refined,
        '</style> </head> ',
        '<body> <div> ',
        block_refined,
        '</div> </body> ',
        '</html> '
    ])

    refined_dict = {note_url: new_html}
    return refined_dict
