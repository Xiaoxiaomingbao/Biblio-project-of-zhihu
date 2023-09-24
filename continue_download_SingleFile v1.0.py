import os
import time
import pyautogui


order = int(input('输入0表示连续下载至书的末尾，输入正整数控制连续下载的总页数（包括初始页）'))
save_path = input('输入HTML保存的文件夹路径')
total_started = int(input('输入开始时文件夹中已有的HTML文件总数'))
# 输入完成后务必立刻将界面切换至电子书的初始页
time.sleep(2)  # 等待一些时间，确保焦点在浏览器界面上


def file_exist(total_expected):
    while True:
        time.sleep(2)
        k = 0
        for f in os.listdir(save_path):
            if f.endswith('.html'):
                k = k + 1
        if k == total_expected:
            return True
        else:
            return False


def num(a):
    if a > 999:
        number = str(a)
    elif a > 99:
        number = '0' + str(a)
    elif a > 9:
        number = '00' + str(a)
    else:
        number = '000' + str(a)
    return number


if order > 0:
    for i in range(order):
        j = i + 1
        print(num(j) + '准备下载')
        while True:
            if file_exist(total_started + j):
                print(num(j) + '完成下载')
                pyautogui.press('right')
                break
            else:
                pass


else:
    i = 0
    while True:
        i = i + 1
        print(num(i) + '准备下载')
        t = 0
        while True:
            if file_exist(total_started + i):
                print(num(i) + '完成下载')
                pyautogui.press('right')
                break
            else:
                pass
            time.sleep(2)
            t = t + 1
            if t > 3:
                print('已到本书末尾，无需再下载')
                exit(0)
