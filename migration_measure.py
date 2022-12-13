

######################################









path = ''

import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog, ttk
from tkinter import messagebox
import os
import cv2
import numpy as np


global root
def newwindow():
    global root,scale,scalethreshup,scalethreshdn,varcheck,imgmask
    if 'imgmask' in globals():
        root = tk.Toplevel(win1)
        root.geometry("1250x950+00+00")
        root.resizable(width=True, height=True)
        root.title("Object Identification")

        botframe = Frame(root)
        botframe.pack(side=BOTTOM)

        Label(root, text="Size").pack(side=TOP)
        var = DoubleVar()
        scale = Scale( root,from_=4.5, to=0.5,resolution=0.02,variable = var, command=viewwin2,orient=HORIZONTAL,length=300 )  # call sel function on change
        scale.set(1)
        scale.pack(side=TOP)

        Label(root, text="Threshold Up",wraplength=1).pack(side=LEFT)
        var2 = DoubleVar()
        scalethreshup = Scale( root,from_=10, to=0,resolution=0.02,variable = var2, command=func2,orient=VERTICAL,length=400 )  # call sel function on change
        scalethreshup.set(10)
        scalethreshup.pack(side=LEFT)

        Label(root, text="Threshold Dn", wraplength=1).pack(side=RIGHT)
        var2 = DoubleVar()
        scalethreshdn = Scale(root, from_=10, to=0, resolution=0.02, variable=var2, command=func2, orient=VERTICAL,length=400)  # call sel function on change
        scalethreshdn.set(0)
        scalethreshdn.pack(side=RIGHT)

        btnsave = Button(root, text='Save Image', width=20, height=3, command=save_img )
        btnsave.pack(in_=botframe,side=LEFT)
    else:
        messagebox.showinfo("Alert", "No image given or \n No process made")


def show_image(image):
    cv2.imshow('image',image)
    c = cv2.waitKey()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    if c >= 0 :
        return -1
    else:
        return 0


win1 = Tk('App')
win1.geometry("2000x1000+00+00")
win1.resizable(width=True, height=True)
win1.title("Object Identification")

topframe = Frame(win1)
topframe.pack(side=TOP)




def hsvfun(imgc,h_up,s_up,v_up,h_dn,s_dn,v_dn,kernelsize,first):
    imgcv = np.array(imgc)
    imgcv = imgcv[:, :, ::-1].copy()  # Convert RGB to BGR
    hsv = cv2.cvtColor(imgcv.copy(), cv2.COLOR_BGR2HSV) # Convert to HSV
    mask2 = cv2.inRange(hsv.copy(), (h_dn,s_dn,v_dn), (h_up,s_up,v_up))
    kernel = np.ones((kernelsize, kernelsize), np.uint8)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel)
    res=cv2.bitwise_or(imgcv, imgcv, mask=mask2)
    res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
    res = Image.fromarray(res)
    percentage=100 * np.count_nonzero(mask2 == 255) / mask2.size
    # print('percentage = ', percentage, ' %')
    return res,mask2,imgcv,percentage


def imgproc(imgc,imgmask,imgorig,varthresholdup,varthresholddn,first):
    imgcv = np.array(imgc)
    imgcv = imgcv[:, :, ::-1].copy()  # Convert RGB to BGR

    (thresh, imgbw) = cv2.threshold(imgmask, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    blurred = imgbw
    edged = cv2.Canny(blurred, 10, 11)

    contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    poly = []
    for i in range(len(contours)):
        cnt = contours[i]
        M = cv2.moments(cnt)
        approx=cv2.convexHull(cnt)
        poly.append(cv2.arcLength(approx, True))

    if len(poly)!=0:
        Middlepolyup = varthresholdup * sum(poly) / len(poly)
        Middlepolydn = varthresholddn * sum(poly) / len(poly)
        newcontours = []
        for i in range(len(contours)):
            if (poly[i] > Middlepolydn and poly[i] < Middlepolyup):
                newcontours.append(contours[i])
    else:
        newcontours=[]



    print('total objects:')
    print(len(newcontours))

    imgcont = imgorig.copy()
    for c in newcontours:
        # compute the center of the contour
        M = cv2.moments(c)
        if (M["m00"] != 0):
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # draw the contour and center of the shape on the image
            cv2.drawContours(imgcont, [c], -1, (20, 250, 20), 2)
            cv2.circle(imgcont, (cX, cY), 3, (255, 255, 255), -1)

    imgcont = cv2.cvtColor(imgcont, cv2.COLOR_BGR2RGB)
    imgcont = Image.fromarray(imgcont)
    return imgcont,len(newcontours)





def openfn():
    global filename

    if 'panel' in globals():
        panel.destroy()

    filename = filedialog.askopenfilename(title='open')
    return filename
def open_img():
    global imgc, imgini
    global panelc,panelperc
    global text
    global first
    first=1
    if 'text' in globals():
        text.destroy()
    if 'percent' in globals():
        panelperc.destroy()

    x = openfn()
    img = Image.open(x)
    scalef=1
    img = img.resize((round(img.width/scalef), round(img.height/scalef)), Image.ANTIALIAS)
    imgc = img
    imgini=img
    img = ImageTk.PhotoImage(imgc)
    panel = Label(win1, image=img)
    panel.image = img
    panelc=panel
    panel.pack()


    #
    # text = Label(root, text="Objects Found: ---")
    # text.pack()


def save_img():
    global No_obj, imgc, filename
    if 'filename' in globals():
        filename_head=os.path.split(filename)[0]
        if 'No_obj' in globals() and No_obj!=0:
            imgc.save(os.path.splitext(filename)[0] + ' Obj=' + str(No_obj) + os.path.splitext(filename)[1])
            messagebox.showinfo("Done", "Image Saved at: \n" + filename_head)
        else:
            messagebox.showinfo("Alert", "No objects found \nImage has not been saved")
    else:
        messagebox.showinfo("Alert", "No image given")







def viewwin1(val=0,panelc2=1):
    # pass new scale value
   #selection = "Value = " + str(var.get())
   #label.config(text = selection)

    global scalef
    global panel
    global imgc
    global text
    global No_obj


    if 'panelc' in globals():
        panelc.destroy()
    if 'panel' in globals():
        panel.destroy()
    if 'text' in globals():
        text.destroy()



    label.config(text = val)
    scalef = float(val)
    print(scalef)


    if 'imgc' in globals():
        img = imgc.resize((round(imgc.width / scalef), round(imgc.height / scalef)), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = Label(win1, image=img)
        panel.image = img
        panel.pack()

        if 'text' in globals():
            text = Label(win1, text="Objects Found: {}".format(No_obj))
            text.pack()


def viewwin2(val=0,panelc2=1):
    global root
    global scalef
    global panel2
    global imgc
    global text
    global No_obj

    if 'panelc' in globals():
        panelc.destroy()
    if 'panel2' in globals():
        panel2.destroy()
    if 'text' in globals():
        text.destroy()

    label.config(text = val)
    scalef = float(val)
    print(scalef)


    if 'imgc' in globals():
        img = imgc.resize((round(imgc.width / scalef), round(imgc.height / scalef)), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel2 = Label(root, image=img)
        panel2.image = img
        panel2.pack()

        if 'text' in globals():
            text = Label(root, text="Objects Found: {}".format(No_obj))
            text.pack()






def func2(val=0,valcol=0,panelc2=1):  # pass new scale value

    global root, scale, scalethreshup,scalethreshdn
    global scalef
    global panel2
    global imgc, imgini, imgmask, imgorig
    global text
    global first
    global No_obj


    if 'panelc' in globals():
        panelc.destroy()
    if 'panel' in globals():
        panel2.destroy()
    if 'text' in globals():
        text.destroy()

    # label.config(text=str(scale2.get()))


    #label.config(text = val)
    thresholdup = float(scalethreshup.get())
    print(thresholdup)
    thresholddn = float(scalethreshdn.get())
    print(thresholddn)

    if 'imgc' in globals():
        imgc,No_obj=imgproc(imgini,imgmask,imgorig,thresholdup,thresholddn,first)

        img = imgc.resize((round(imgc.width / scalef), round(imgc.height / scalef)), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel2 = Label(root, image=img)
        panel2.image = img
        panel2.pack()

        text = Label(root, text="Objects Found: {}".format(No_obj))
        text.pack()


# def checkfunc():
#     global first,varcheck
#     if varcheck.get()==1:
#         first=0
#     else:
#         first=1


def mainfun(var=0, hvarup=0,svarup=0,vvraup=0,hvardn=0,svardn=0,vvradn=0,varkersize=0):
    global scalef
    global panel, panelperc
    global imgc, imgini, imgmask,imgorig,percent
    global text
    global first
    global No_obj

    if 'panelc' in globals():
        panelc.destroy()
    if 'panel' in globals():
        panel.destroy()
    if 'text' in globals():
        text.destroy()
    if 'percent' in globals():
        panelperc.destroy()

    # label.config(text=str(scale2.get()))

    h_up =int(scale1.get())
    s_up =int(scale2.get())
    v_up =int(scale3.get())
    h_dn =int(scale4.get())
    s_dn =int(scale5.get())
    v_dn =int(scale6.get())
    kernelsize=int(kersize.get())


    if 'imgc' in globals():
        imgc, imgmask,imgorig,percent = hsvfun(imgini, h_up,s_up,v_up,h_dn,s_dn,v_dn,kernelsize,first)

        img = imgc.resize((round(imgc.width / scalef), round(imgc.height / scalef)), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = Label(win1, image=img)
        panel.image = img
        panel.pack()

        perctext='Percentage = '+ str(round(percent,3))+ '%'+', (excluded='+str(round(100-percent,3))+ '%)'
        panelperc=Label(win1, text=perctext)
        panelperc.pack(in_=topframe, side=LEFT)



L=400
R=0.01

btn = Button(win1, text='Load Image',width=20,height=3, command=open_img)
btn.pack(in_=topframe, side=LEFT)

btn = Button(win1, text='Next',width=20,height=3, command=newwindow)
btn.pack(in_=topframe, side=LEFT)


# varcheck = tk.IntVar()
# c1 = tk.Checkbutton(win1, text='Reduce Size', variable=varcheck, onvalue=1, offvalue=0, command=checkfunc)
# c1.pack(in_=topframe, side=LEFT)


Label(win1, text="Size").pack()
var = DoubleVar()
scale = Scale(win1,from_=4.5, to=0.5,resolution=0.02,variable = var, command=viewwin1,orient=HORIZONTAL,length=300,showvalue=0)  # call sel function on change
scale.set(1)
scale.pack(side=TOP)

Label(win1, text="Kernel Size").pack(side=BOTTOM)
varkersize = DoubleVar()
kersize = Scale(win1,from_=1, to=7,resolution=1,variable = varkersize, command=mainfun,orient=HORIZONTAL,length=100)  # call sel function on change
kersize.set(2)
kersize.pack(side=BOTTOM)

Label(win1, text="HueUP",wraplength=1).pack(side=LEFT)
hvarup = DoubleVar()
scale1 = Scale( win1,from_=0, to=180,resolution=R,variable = hvarup, command=mainfun,orient=VERTICAL,length=L)  # call sel function on change
scale1.set(180)
scale1.pack(side=LEFT)

Label(win1, text="SatUP",wraplength=1).pack(side=LEFT)
svarup = DoubleVar()
scale2 = Scale( win1,from_=0, to=255,resolution=R,variable = svarup, command=mainfun,orient=VERTICAL,length=L)  # call sel function on change
scale2.set(255)
scale2.pack(side=LEFT)

Label(win1, text="ValueUP",wraplength=1).pack(side=LEFT)
vvarup = DoubleVar()
scale3 = Scale( win1,from_=0, to=255,resolution=R,variable = vvarup, command=mainfun,orient=VERTICAL,length=L )  # call sel function on change
scale3.set(255)
scale3.pack(side=LEFT)

Label(win1, text="HueDN",wraplength=1).pack(side=RIGHT)
hvardn = DoubleVar()
scale4 = Scale( win1,from_=0, to=180,resolution=R,variable = hvardn, command=mainfun,orient=VERTICAL,length=L )  # call sel function on change
scale4.set(0)
scale4.pack(side=RIGHT)

Label(win1, text="SatDN",wraplength=1).pack(side=RIGHT)
svardn = DoubleVar()
scale5 = Scale( win1,from_=0, to=255,resolution=R,variable = svardn, command=mainfun,orient=VERTICAL,length=L )  # call sel function on change
scale5.set(0)
scale5.pack(side=RIGHT)

Label(win1, text="ValueDN",wraplength=1).pack(side=RIGHT)
vvardn = DoubleVar()
scale6 = Scale( win1,from_=0, to=255,resolution=R,variable = vvardn, command=mainfun,orient=VERTICAL,length=L )  # call sel function on change
scale6.set(0)
scale6.pack(side=RIGHT)


label = Label(win1)
# label.pack() # comment gia na mh fainetai o arithmos



win1.mainloop()




