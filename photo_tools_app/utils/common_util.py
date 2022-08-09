# -*- coding: utf-8 -*-

import base64
from photo_tools_app.__init__ import app


# def hashCode(s):
#     seed = 31
#     h = 0
#     for c in s:
#         h = int32(seed * h) + ord(c)
#     return h
class GetHashCode:
    """
    类似 Java中hashcode函数
    java实现：
        ID = String.valueOf(Math.abs((this.OMC_IP + this.FTP_PORT + this.FILE_PATH).hashCode()))
    """
    def convert_n_bytes(self, n, b):
        bits = b * 8
        return (n + 2 ** (bits - 1)) % 2 ** bits - 2 ** (bits - 1)

    def convert_4_bytes(self, n):
        return self.convert_n_bytes(n, 4)

    @classmethod
    def getHashCode(cls, s):
        h = 0
        n = len(s)
        for i, c in enumerate(s):
            h = h + ord(c) * 31 ** (n - 1 - i)
        return cls().convert_4_bytes(h)


def getUploadDirs(name):
    if not name:
        return False
    code = GetHashCode.getHashCode(name)
    # 第一层目录
    first_dir = '{:x}'.format(code & 0xf)
    # 第二层目录
    second_dir = '{:x}'.format((code >> 4) & 0xf)
    return first_dir, second_dir


def imageToBase64(imagePath):
    with open(imagePath, 'rb') as f:
        image = base64.b64encode(f.read())
        return str(image, encoding='utf-8')


""" 读取图片 """
def getFileContent(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 用于判断文件后缀
def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


if __name__ == "__main__":
    print(getUploadDirs('a.jpg'))