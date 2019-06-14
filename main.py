from datetime import datetime, timedelta
from time import time, sleep
import itertools

import pygame

import os.path

import numpy as np
from geopy import distance

from orbit_np import Orbitals , bearingBetween
from opensky import OpenSkyApi

from credentials import OPENSKY_PASSWD, OPENSKY_USER

def coordsFromPolar(centre,anglefromnorm,dist):
    x = centre[0] + 4*dist*np.cos(anglefromnorm)
    y = centre[1] + 4*dist*np.sin(anglefromnorm)
    
    return x, y
def bearingBetween(lat1,long1,lat2,long2):
    '''
    Returns angle from normal (x-axis) in radians to get from a to b, in lat longs
    '''
    
    lat1 , long1 = np.deg2rad(lat1) , np.deg2rad(long1)
    lat2 , long2 = np.deg2rad(lat2) , np.deg2rad(long2)
    dLong =  long2 - long1

    y = np.sin(dLong) * np.cos(lat2)
    x = ( np.cos(lat1) * np.sin(lat2) - 
         np.sin(lat1) * np.cos(lat2) * np.cos(dLong) )

    bearing = np.arctan2(y,x)
    return bearing - np.pi/2


def filterAC(acs):
    return [ac for ac in acs if not ac[4]]

 
HERE = (53.256118, -1.911817)  # lat long

d = distance.distance(kilometers=150)
mincorner = d.destination(point=HERE, bearing=225)
maxcorner = d.destination(point=HERE, bearing=45)
acBound = (mincorner[0],maxcorner[0],mincorner[1],maxcorner[1])



pygame.init()


screen = pygame.display.set_mode((600,680))
pygame.display.set_caption("Aircraft Tracker")

myfont = pygame.font.SysFont('monospace', 14)

centre = (300,300)

clock = pygame.time.Clock()
done = False
RED = (255,0,0)
MGREY = (153,153,153)
GREEN = (0,204,0)
BLUE = (0,0,230)

showAC = True

osapi = OpenSkyApi(username=OPENSKY_USER,password=OPENSKY_PASSWD)

localACdata = []

nextacfetch = datetime.now()

nextupdate = datetime.now()

while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
           
            if event.key == pygame.K_a:
                showAC = not showAC

    if not datetime.now() < nextupdate:
        screen.fill((0,0,0))
        # ---------- UI ---------------
        pygame.draw.line(screen,MGREY,(0,600),(600,600))

        

        
        

        labelAC = myfont.render("All Aircraft - Press a to toggle", 1, MGREY)
        screen.blit(labelAC, (77 , 638) )

        labelhere = myfont.render("BUX", 1, MGREY)
        screen.blit(labelhere, (285 , 302) )


        pygame.draw.line(screen,MGREY,(300,300),(300,50))
        labeln = myfont.render('North', 1, MGREY)
        screen.blit(labeln, (302 , 50) )

        pygame.draw.circle(screen,MGREY,centre,200,1)
        label50 = myfont.render('50km', 1, MGREY)
        screen.blit(label50, (351+150 , 300) )

        

        # --------- Aircraft
        if not datetime.now() < nextacfetch:
            #print("updating ac data")
            localACdata = osapi.get_locallatlongalt(acBound)
            nextacfetch = datetime.now() + timedelta(seconds = 5)
            for idx,ac in enumerate(filterAC(localACdata)):
                angletoAC = bearingBetween(HERE[0],HERE[1],ac[1],ac[2])
                disttoAC = distance.distance(HERE,(ac[1],ac[2])).km
                localACdata[idx].append(disttoAC)
            array = np.array(localACdata)[:,5]
            array = array.astype(float)
            min = np.argmin(array)
            #print(localACdata[min][0],localACdata[min][5])
            nearestAC = localACdata[min]
            angletoNearestAC = bearingBetween(HERE[0],HERE[1],nearestAC[1],nearestAC[2])
            print(nearestAC[0])
            print(np.rad2deg(angletoNearestAC)+180)
        
        for idx,ac in enumerate(filterAC(localACdata)):
            angletoAC = bearingBetween(HERE[0],HERE[1],ac[1],ac[2])
            disttoAC = ac[5]
            x , y = coordsFromPolar(centre,angletoAC,disttoAC)
            pygame.draw.rect(screen,BLUE,(x,y,5,5))
            labelname = myfont.render(ac[0], 1, BLUE)
            labelalt = myfont.render(str(ac[3]*3.28084)[:5]+'ft', 1, BLUE)
            screen.blit(labelname, (x +5 ,y +5) )
            screen.blit(labelalt, (x +5 ,y +20) )
        

        
        nextupdate = datetime.now() + timedelta(seconds=0.3) 
        pygame.display.flip()
        


    clock.tick(30)