import cv2 as cv
import numpy as np
vid = cv.VideoCapture(0)
cascade = cv.CascadeClassifier( cv.data.haarcascades +'haarcascade_frontalface_default.xml')
if not vid.isOpened():
    print("Impossible d'ouvrir la video")
    exit()
#dans le cas ou la video est ouverte on capture frame par frame
while vid.isOpened():
#capture frame-by-frame
    _, frame = vid.read()#read return true or false
   #if frame is corectly captured ret is true
    
    #Convertir la couleur en gris 
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #Les faces 
    faces = cascade.detectMultiScale(gray,1.1, 4)
    for (x,y,z,w) in faces:
        cv.rectangle(frame,(x,y),(x+w,y+z),(255,0,0), 4)
    cv.imshow('WebCam',frame)
    if cv.waitKey(1) == ord('q'):
        """
         si je met 1 = la video marche toute seule
         0,-1 : interupption 
        """
        break
#Feremr la camera
vid.release()
cv.destroyAllWindows()
