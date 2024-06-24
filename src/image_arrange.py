import base64
import re
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


def arrange(html_path, images_path, accu):
    pat_data = re.compile(r'<img[^>]+src\s?=\s?[\'"]?([^\'">]+)[^>]*>')
    pat = re.compile(r'data:image/([a-zA-Z]+);base64,([^>\s]+)')
    # 有的书含有svg图片，能匹配上第一个模式，但匹配不上第二个模式，不予处理，但会计入图片编号
    with open(html_path, 'r', encoding='UTF-8') as f:
        html_content = f.read()
    end = 0
    temp = ''
    for match in pat_data.finditer(html_content):
        accu = accu + 1
        raw_data = match.group(1)

        if 'base64' not in raw_data:
            continue

        match1 = pat.search(raw_data)
        img_type = match1.group(1)
        data = match1.group(2)

        img_name = 'image' + format_num(accu) + '.' + img_type
        img_path = os.path.join(images_path, img_name)
        data_bytes = data.encode("utf-8")
        decoded_bytes = base64.b64decode(data_bytes)
        with open(img_path, 'wb') as f:
            f.write(decoded_bytes)
        print('已提取出图片：' + img_name)
        start = match.start(1)
        # 使用上一次的end和这一次的start，第一次end使用前定为0
        temp = temp + html_content[end:start]
        img_path = os.path.join('../..', 'Images', img_name)
        temp = temp + img_path
        end = match.end(1)

    # 上个循环中已经开始更改HTML文件中的img标签
    start = len(html_content)
    new_html_content = temp + html_content[end:start]

    with open(html_path, 'w', encoding='UTF-8') as f:
        f.write(new_html_content)
    return accu
