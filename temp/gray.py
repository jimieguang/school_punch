from cmath import pi
from PIL import Image, ImageFilter

def convert_gray(num):
    image = Image.open(f"standard_{num}.png")
    w, h = image.size
    array = image.load()
    sum = 0
    for i in range(0,w):
        for j in range(0,h):
            sum += array[i,j]

    mean = sum / (w*h)
    for i in range(0,w):
        for j in range(0,h):
            pixel = array[i,j]
            if pixel < mean:
                pixel = 0
            else:
                pixel = 255
            image.putpixel((i,j),pixel)
    image.save(f"res_{num}.png")

def relight(num):
    '''统一八个区域的亮度'''
    image = Image.open(f"target_{num}.jpg").resize((320,160)).convert("L")
    w, h = image.size
    array = image.load()
    sum = 0
    for i in range(0,w):
        for j in range(0,h):
            sum += array[i,j]
    # 整体亮度
    mean = sum / (w*h)
    order = 0
    while order < 8:
        h_scale = int(order/4)
        w_scale = order%4
        temp_sum = 0
        for j in range((int(h/2)*h_scale),int((h/2)*(h_scale+1))):
            for i in range(int((w/4)*w_scale),int((w/4)*(w_scale+1))):
                temp_sum += array[i,j]
        temp_mean = temp_sum / (w*h/8)
        try:
            scale = mean / temp_mean
        except ZeroDivisionError:
            scale = 1
        for j in range((int(h/2)*h_scale),int((h/2)*(h_scale+1))):
            for i in range(int((w/4)*w_scale),int((w/4)*(w_scale+1))):
                image.putpixel((i,j),int(array[i,j]*scale))
        order += 1
    image.save(f"standard_{num}.png")

def find_edge(num):
    image = Image.open(f"target_{num}.jpg").convert("L")
    # image = Image.open(f"res_{num}.png").convert("L")
    image = image.filter(ImageFilter.EDGE_ENHANCE)
    image = image.filter(ImageFilter.FIND_EDGES)
    image.save(f"edge_{num}.png")

def detect(num):
    image = Image.open(f"edge_{num}.png")
    w, h = image.size
    array = image.load()
    # 去除外边缘
    for i in range(w):
        array[i,0] = 0
        array[i,h-1] = 0
    for j in range(h):
        array[0,j] = 0
        array[h-1,j] = 0
    order = 0
    weights = [0 for i in range(8)]
    bias_list = [0,3,4,7] #双边缘区域
    temp = 0
    while order < 8:
        h_scale = int(order/4)
        w_scale = order%4
        x_edge_sum = 0
        yl_edge_sum = 0
        yr_edge_sum = 0
        for i in range(int((w/4)*w_scale),int((w/4)*(w_scale+1))):
            x_edge_sum += array[i,int(h/2)] / 128
        for j in range((int(h/2)*h_scale),int((h/2)*(h_scale+1))):
            yl_edge_sum += array[int((w/4)*w_scale),j] / 128
            try:
                yr_edge_sum += array[int((w/4)*(w_scale+1)),j] / 128
            except IndexError:
                pass
        
        if order in bias_list:
            weights[order] =  (x_edge_sum + yl_edge_sum + yr_edge_sum) / 2
        else:
            weights[order] =  (x_edge_sum + yl_edge_sum + yr_edge_sum) / 3
        order += 1
    print(weights)
    maximum = max(weights)
    print(weights.index(maximum))
    weights[weights.index(maximum)] = 0
    maximum = max(weights)
    print(weights.index(maximum))

            
num = 20
while num <30:
    # relight(num)
    # convert_gray(num)
    find_edge(num)
    detect(num)
    num+=1
            