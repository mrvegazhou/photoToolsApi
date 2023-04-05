# _*_ coding: utf-8 _*_

from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageChops
import math
import os
from blind_watermark import WaterMark


class Watermark:
    """
    1：左上
    2：右上
    3：右下
    4：左下
    5: 中间
    """
    position = 3
    """
    1：华文楷体
    2：方正黑体简体
    3：青鸟华光简琥珀
    """
    fontTTFs = {
        1:'../../uploads/static/wechat/font/华文楷体.ttf',
        2:'../../uploads/static/wechat/font/方正黑体简体.ttf',
        3:'../../uploads/static/wechat/font/font/青鸟华光简琥珀.ttf'
    }
    ttf = 1

    # 添加铺满文字水印
    @staticmethod
    def addFullTextWatermark(imgPath, txt, fontsize=25, color='#000000', space=60, angle=30, opacity=0.4, out=''):
        im = Image.open(imgPath)
        # 字体宽度
        width = len(txt) * fontsize
        # 创建水印图片(宽度、高度)
        mark = Image.new(mode='RGBA', size=(width, fontsize))
        # 生成文字
        draw_table = ImageDraw.Draw(im=mark)
        draw_table.text(xy=(0, 0),
                        text=txt,
                        fill=color,
                        font=ImageFont.truetype(Watermark.fontTTFs[Watermark.ttf], size=fontsize))
        del draw_table
        mark = Watermark.cropImage(mark)
        Watermark.setOpacity(mark, opacity)

        image = Watermark.markOnImg(im, mark, space, angle)

        if image:
            name = os.path.basename(imgPath)
            newName = os.path.join(out, name)
            if os.path.splitext(newName)[1] != '.png':
                image = image.convert('RGB')
            image.save(newName)

    # 添加一个文字水印
    @staticmethod
    def addOneTextWatermark(imgPath, txt, fontsize=25, color='#000000', opacity=0.4, out=''):
        position_list = [1, 2, 3, 4, 5]
        if Watermark.position not in position_list:
            Watermark.position = 1
        im = Image.open(imgPath)
        h, w = im.size[:2]
        fnt = ImageFont.truetype(Watermark.fontTTFs[Watermark.ttf], fontsize)
        im = im.convert('RGBA')
        mask = Image.new('RGBA', im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(mask)
        size_h, size_w = d.textsize(txt, font=fnt)
        alpha = 5
        if Watermark.position == 1:
            pos = (0 + alpha, 0 + alpha)
        elif Watermark.position == 2:
            pos = (h - size_h - alpha, 0 + alpha)
        elif Watermark.position == 3:
            pos = (h - size_h - alpha, w - size_w - alpha)
        elif Watermark.position == 4:
            pos = (0 + alpha, w - size_w - alpha)
        else:
            pos = ((h - size_h)/2, (w - size_w)/2)
        d.text(pos, txt, font=fnt, fill=color)
        mask = Watermark.setOpacity(mask, opacity)
        outImg = Image.alpha_composite(im, mask)
        name = os.path.basename(imgPath)
        newName = os.path.join(out, name)
        if os.path.splitext(newName)[1] != '.png':
            outImg = outImg.convert('RGB')
        outImg.save(newName)
        # outImg.show()

    # 裁剪图片边缘空白
    @staticmethod
    def cropImage(im):
        bg = Image.new(mode='RGBA', size=im.size)
        diff = ImageChops.difference(im, bg)
        del bg
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)
        return im

    # 设置水印透明度
    @staticmethod
    def setOpacity(im, opacity):
        assert opacity >= 0 and opacity <= 1

        alpha = im.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        im.putalpha(alpha)
        return im


    # 在im图片上添加水印 im为打开的原图
    @staticmethod
    def markOnImg(im, mark, space, angle):
        # 计算斜边长度
        c = int(math.sqrt(im.size[0] * im.size[0] + im.size[1] * im.size[1]))
        # 以斜边长度为宽高创建大图（旋转后大图才足以覆盖原图）
        mark2 = Image.new(mode='RGBA', size=(c, c))
        # 在大图上生成水印文字，此处mark为上面生成的水印图片
        y, idx = 0, 0
        while y < c:
            # 制造x坐标错位
            x = -int((mark.size[0] + space) * 0.5 * idx)
            idx = (idx + 1) % 2

            while x < c:
                # 在该位置粘贴mark水印图片
                mark2.paste(mark, (x, y))
                x = x + mark.size[0] + space
            y = y + mark.size[1] + space

        # 将大图旋转一定角度
        mark2 = mark2.rotate(angle)

        # 在原图上添加大图水印
        if im.mode != 'RGBA':
            im = im.convert('RGBA')

        im.paste(mark2,  # 大图
                 (int((im.size[0] - c) / 2), int((im.size[1] - c) / 2)),  # 坐标
                 mask=mark2.split()[3])
        del mark2
        return im



    # 添加一个logo水印
    @staticmethod
    def addOneLogoWatermark(imgPath, logoPath, out='', opacity=0.4):
        image = Image.open(imgPath)
        logo = Image.open(logoPath)
        width = image.width
        height = image.height
        (markWidth, markHeight) = logo.size

        logo = logo.convert("RGBA")
        if width/3 < markWidth and height/3 < markHeight:
            w = int(width/4)
            h = int(height/4)
        elif width/3 > markWidth and height/3 > markHeight:
            w = markWidth
            h = markHeight
        else:
            w = int(width / 2)
            h = int(height / 2)
        logo = logo.resize((w, h))
        # add transparency to logo
        logo = Watermark.setOpacity(logo, opacity)

        watermark = Image.new('RGB', image.size, (0, 0, 0))
        watermark.paste(image, (0, 0))

        position = Watermark.getPosition(watermark, logo)
        watermark.paste(logo, position, mask=logo)

        name = os.path.basename(imgPath)
        newName = os.path.join(out, name)
        # watermark.save(newName)
        watermark.show()

    @staticmethod
    def addFullLogoWatermark(imgPath, logoPath, out='', space=60, angle=30, opacity=0.4):
        im = Image.open(imgPath)
        mark = Image.open(logoPath)
        (width, height) = im.size
        mark = mark.convert("RGBA")
        (markWidth, markHeight) = mark.size
        if width/3 < markWidth and height/3 < markHeight:
            w = int(width/4)
            h = int(height/4)
        elif width/3 > markWidth and height/3 > markHeight:
            w = markWidth
            h = markHeight
        else:
            w = int(width / 2)
            h = int(height / 2)
        mark = mark.resize((w, h))
        Watermark.setOpacity(mark, opacity)
        image = Watermark.markOnImg(im, mark, space, angle)
        image.show()

    # 添加一个logo水印2
    @staticmethod
    def addOneLogoWatermark2(imgPath, logoPath, out='', opacity=0.4):
        """
        Method 2: Method to watermark photos using the Image.alpha_composite
        """
        base_image = Image.open(imgPath).convert("RGBA")
        transparent = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
        (width, height) = base_image.size
        logo_image = Image.open(logoPath)
        logo_image = logo_image.resize((int(width / 2), int(height / 2)))
        logo_image = Watermark.addImageTransparency(logo_image)
        position = Watermark.getPosition(transparent, logo_image)
        transparent.paste(logo_image, position, mask=logo_image)
        # Instead of pasting one image over another we can also use alpha_composite to put images on layers
        watermarked = Image.alpha_composite(base_image, transparent)
        name = os.path.basename(imgPath)
        newName = os.path.join(out, name)
        watermarked.save(newName)


    @staticmethod
    def addImageTransparency(image, alpha=30):
        # To add transparency we need to make non zero alpha pixels to given alpha value.
        image_alpha = image.getchannel('A')
        new_alpha = image_alpha.point(lambda i: alpha if i > 0 else 0)
        image.putalpha(new_alpha)
        return image

    @staticmethod
    def getPosition(image, logo):
        # Get the center positions of image for image2
        width, height = image.size
        width2, height2 = logo.size

        alpha = 5
        if Watermark.position == 1:
            pos = (alpha, alpha)
        elif Watermark.position == 2:
            pos = (alpha, height - height2 - alpha)
        elif Watermark.position == 3:
            pos = (width - width2 - alpha, height - height2 - alpha)
        elif Watermark.position == 4:
            pos = (width - width2 - alpha, alpha)
        else:
            x = (width - width2) / 2
            y = (height - height2) / 2
            pos = (x, y)
        return pos


    # 盲水印
    @staticmethod
    def addBlindWatermark(imagePath, secret='123', out='', type=1, waterImgPath=''):
        ## 设置密码，默认是 1
        bwm1 = WaterMark(password_img=1, password_wm=1)

        ## 读取原始图片
        bwm1.read_img(imagePath)
        if type==1:
            ## 合并文本并输出新的图片
            bwm1.read_wm(secret, mode='str')
        else:
            ## 读取水印图片
            bwm1.read_wm(waterImgPath)
        bwm1.embed(out)


    @staticmethod
    def getBlindWatermarkInfo(path, txt='', type=1, out=''):
        bwm1 = WaterMark(password_img=1, password_wm=1)
        if type==1:
            wm_extract = bwm1.extract(path, wm_shape=len(txt), mode='str')
            return wm_extract
        else:
            bwm1.extract(filename=path, wm_shape=(128, 128), out_wm_name=out )


if __name__ == "__main__":

    image = '/Users/vega/workspace/codes/py_space/working/photo-tools-api/photo_tools_app/service/shuiyin.png'
    image2 = '/Users/vega/workspace/codes/py_space/working/photo-tools-api/photo_tools_app/service/rrrr.png'
    Watermark.position = 3
    Watermark.addOneLogoWatermark(image, image2, out='./')


