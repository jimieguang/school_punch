#jpg格式是有损压缩，代码中引入的判定像素可能会变化导致一系列不确定后果，因此使用png格式保存匹配图片
from PIL import Image
def find_pic(order):
    '''匹配缺口'''
    image1 = Image.open("./text/new%d.jpg"%order)
    image2 = Image.open("target.jpg")

    image3 = Image.new("RGB",(320,160),(255,255,255))
    num = 0
    for i in range(0,320):
        for j in range(0,160):
            r1,g1,b1 = image1.getpixel((i,j))
            r2,g2,b2 = image2.getpixel((i,j))
            if r1 !=0:
                scale = r2/r1
                if scale < 0.9:
                    num += 1
                    image3.putpixel((i,j),(0,0,0,0))
                if  scale>1.1:
                    num += 1
                    image3.putpixel((i,j),(126,0,0,0))
    if num < 4000:
        image3.save("result-%d.png"%order)
        return order
    else:
        return 0

def find_distance(fileorder):
    '''找到缺口离起点的距离（像素）'''
    image = Image.open("result-%d.png"%fileorder)
    #对第三张图片的特殊照顾
    if fileorder == 3:
        judgelist = [0]
    else:
        judgelist = [0,126]
    for i in range(0,320):
        num = 0
        for j in range(0,160):
            r1,g1,b1 = image.getpixel((i,j))
            if r1 in judgelist:
                num += 1
        if num > 20:
            return i
    return 0

if __name__ == "__main__":
    for i in range(1,6):
        fileorder = find_pic(i)
        if fileorder != 0:
            break
    distance = find_distance(fileorder)
    print("distance=%d"%distance)

