import os


def format_num(number):
    if number > 999:
        return str(number)
    elif number > 99:
        return '0' + str(number)
    elif number > 9:
        return '00' + str(number)
    else:
        return '000' + str(number)


# 这个递归调用很特别，每次都在前一个的基础上加一些内容，事实上，历次函数调用的返回值都一样
def set_navpoint(nav,contents,order):
    content = contents[order]
    level = int(content[1][-1:])
    order = order + 1
    np_id = 'navPoint' + str(order)
    np = '<navPoint id="' + np_id + '" playOrder="' + str(order) + '">'
    nl = '<navLabel><text>' + content[0] + '</navLabel></text>'
    pre_path = 'part' + format_num(order) + '.html'
    path = 'Text/' + pre_path
    ct = '<content src="' + path + '"/>'
    if order < len(contents):
        content = contents[order]
        new_level = int(content[1][-1:])
        if new_level > level:
            base = nav + np + nl + ct
            return set_navpoint(base,contents,order)
        elif new_level == level:
            base = nav + np + nl + ct + '</navPoint>'
            return set_navpoint(base,contents,order)
        else:
            base = nav + np + nl + ct + '</navPoint>'
            for k in range(level - new_level):
                base = base + '</navPoint>'
            return set_navpoint(base,contents,order)
    else:
        base = nav + np + nl + ct + '</navPoint>'
        return base
    

def set_the_ncx(contents,folder):
    ncx = '''
    <?xml version='1.0' encoding='utf-8'?>
<ncx>
  <head>
    <meta content="Biblio Project" name="dtb:generator"/>
    <meta content="0" name="dtb:totalPageCount"/>
    <meta content="0" name="dtb:maxPageNumber"/>
  </head>
    '''
    title = input('输入书名（docTitle）')
    ncx = ncx + '<docTitle>' + '<text>' + title + '</text>' + '</docTitle>'
    navmap = '<navMap>'
    order = 0
    navmap = set_navpoint(navmap,contents,0)
    navmap = navmap + '</navMap>'
    ncx = ncx + navmap + '</ncx>'

    path = os.path.join(folder,'OEBPS','toc.ncx')
    with open(path,'w',encoding='UTF-8') as f:
        f.write(ncx)
    
