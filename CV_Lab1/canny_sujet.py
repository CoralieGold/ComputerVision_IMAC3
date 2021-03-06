#!/usr/bin/python
# -*- coding: utf-8 -*-
# Attentions : faire adjustments necessaires pour les differentes versions de Python


import numpy as np
import scipy.ndimage
from scipy import ndimage, misc
import pickle
import matplotlib.pyplot as plt
# canny

def pause():
    """this function allows to refresh a figure and do a pause"""
    plt.draw() 
    #plt.pause(0.001)
    plt.pause(1)
    
def plotImageWithColorBar(I,cmap=plt.cm.Greys_r,title=''): 
    """this function displays an image and a color bar"""
    fig = plt.figure(figsize=(8,7))
    ax=plt.subplot(1,1,1)
    plt.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0)
    implot=plt.imshow(I,cmap)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.colorbar(implot, use_gridspec=True)    
    plt.title(title)
    
def displayImageAndVectorField(I,vx,vy,step,color):
    """this function displas an image with an overlaid vector field"""
    assert (vx.shape==vy.shape)
    assert (I.shape==vy.shape)
    fig = plt.figure(figsize=(8,7))
    ax=plt.subplot(1,1,1)
    plt.imshow(I,cmap=plt.cm.Greys_r)    
    X,Y = np.meshgrid( np.arange(0,I.shape[1]),np.arange(0,I.shape[0]) )
    plt.quiver(X[::step,::step],Y[::step,::step],vx[::step,::step],-vy[::step,::step],color=color) 
    # dansd le cas où l'on affiche une image on a besoinf d'inverser la direction y , étrange ...
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0)
    
    
def sampleImage(I,x,y):
    """cette fonction permet de sampler une image en niveau de gris 
    en un ensemble de positions discrètes fournies dans deux matrices 
    de même dimension mxn le resultat est de taille mxn
    samples[i,j]=I[y[i,j],x[i,j]]"""
    x=x.astype(int)
    y=y.astype(int) 
    assert np.all(x.shape==y.shape)  
    return I[y,x] # see http://docs.scipy.org/doc/numpy/user/basics.indexing.html#indexing-multi-dimensional-arrays

def smoothGaussian(im,sigma):
    # TODO:
    # implementez un  lissage de l'image en utilisant un noyau gaussien avec un déviation standard de sigma  
    # prenez un taille de noyeau de 3*sigma de chaque coté du centre 
    # n'oubliez de convertir l'image en float avant de faire la convolution avec im=im.astype(float)  
    # n'utilisez pas de fonction toute faite pour obtenir le noyau gaussien ,
    # vous pouvez utiliser np.meshgrid (utilisée dans la fonction displayImageAndVectorField ci dessus) avec la fonction np.arange
    # attention np.arange(a,b) donne des nombres allant de a à b-1 et non de a à b 
    # pour créer deux tableau 2D carrées X et Y de taille 2N+1 avec X[i,j]=j-N et Y[i,j]=i-N avec N=*3*sigma
    # puis utilisez les operateur **2 et np.exp sur ces tableau pour obtenir une image de gaussienne centree en (N,N)
    # affichez cette image avec plt.imshow(gaussienne)
    # si l'image semble quantifiée  c'est parceque vous avez oublié de convertir X et Y en float avec X=X.astype(float) et Y=Y.astype(float)  
    # avant de faire une division 
    # verifiez numériquement la symétrie de votre gaussienne 
    # vous pouvez implémenter une autre version qui tire avantage de la séparabilité du filtre
    
    # IMPLEMENTATION : Fonctionne
    im = im.astype(float)
    N = 3*sigma
    X,Y = np.meshgrid(np.arange(-2*N, 2*N+1),np.arange(-2*N, 2*N+1))
    X = X.astype(float)
    Y = Y.astype(float)
    
    gaussienne = np.exp(-0.333*(X**2/float(2*N)+Y**2/float(2*N)))
    gaussienne = gaussienne/gaussienne.sum()
    
    # plt.imshow(gaussienne)
    # pause()

    im_smooth = scipy.ndimage.convolve(im, gaussienne)
    return im_smooth
   
def gradient(im_smooth):
    # TODO:
    # utilisez scipy.ndimage.convolve pour calculer le gradient de l'image 
    # assurez vous d'avoir péalablement converti l'image en float sans quoi vous n'aurez pas le résultat souhaité
    # verifiez que vous avez n'avez pas calculé le vecteur inverse du gradient i.e que le flèches pointent bien vers les zones plus claires
    # lorsque vous executez displayImageAndVectorField(im_smooth,gradient_x,gradient_y,10,'b')  
    # ...  
    
    # IMPLEMENTATION :
    
    # From https://en.wikipedia.org/wiki/Sobel_operator
    filter_sobel_x = np.array([[1, 0, -1],[2, 0, -2],[1, 0, -1]]).astype(float)
    filter_sobel_y = np.array([[1, 2, 1],[0, 0, 0],[-1, -2, -1]]).astype(float)
    gradient_x = scipy.ndimage.convolve(im_smooth.astype(float), filter_sobel_x)
    gradient_y = scipy.ndimage.convolve(im_smooth.astype(float), filter_sobel_y)

    displayImageAndVectorField(im_smooth,gradient_x,gradient_y,10,'b')
    #pause()

    return gradient_x,gradient_y

def gradientNormeEtAngle(gradient_x,gradient_y):
    # TODO:
    # calculez la norm du gradient pour chaque pixel
    # et utilisez la fonction np.arctan2 pour calculer l'angle du gradient pour chaque pixel, attention l'ordre des deux argument est important
    # ...  
    
    #IMPLEMENTATION
    angle = np.arctan2(gradient_y, gradient_x)
    norm_gradient = np.sqrt(gradient_y**2+gradient_x**2)
    return  norm_gradient,angle

def approxAngleEtDirection(angle): 
    # TODO:
    # arrondissez chaque angle donné à l'angle multiple de pi/4 le plus proche (multipliez par 4/pi , arrondissez , puis remultipliez par pi/4)
    # puis arrondissez pour chaque pixel le vecteur unitaire [cos(angle_rounded),sin(angle_rounded)] 
    # au vecteur à coordonnée entières le plus proche i.e. dans [1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]
    # pour obtenir deux images direction_x et direction_y
    # avec [direction_x[i,j],direction_y[i,j]] le vecteur à coordonnées entière le plus proche de [cos(angle_rounded[i,j]),sin(angle_rounded[i,j])] 
    # essayez d'utiliser le caclul matriciel pour éviter de faire des boucles sur les pixels
    # Completez ici  
    
    # IMPLEMENTATION : pas sur
    angle_rounded = np.round(angle * 4/np.pi) * 4/np.pi

    direction_x = np.cos(angle_rounded)
    direction_y = np.sin(angle_rounded)
    
    # FIN IMPLEMENTATION
    
    # ces lignes permettent d'éviter de sortir de l'image dans la fonction localMaximum
    direction_x[:,0]=0 
    direction_x[:,-1]=0
    direction_y[0,:]=0
    direction_y[-1,:]=0    
    return angle_rounded,direction_x,direction_y 
    
def localMaximum(norm_gradient,direction_x,direction_y):
    # TODO:
    # ecrivez cette fonction qui renvoi une image binaire avec maxi[i,j]==True si le pixel (i,j) et un 
    # maximum local dans la direction donnée par direction _x et direction_y
    # i.e si norm_gradient[i,j]>=norm_gradient[i+direction_y[i,j],j+direction_x[i,j]]
    #    et  norm_gradient[i,j]>=norm_gradient[i-direction_y[i,j],j-direction_x[i,j]] 
    # essayer de vectorizer cette fonction pour éviter de faire une boucle sur les pixels
    # en utilisant X,Y,direction_x , direction_y et  la fonction sampleImage définie plus haut 
    
    X,Y = np.meshgrid( np.arange(0,norm_gradient.shape[1]),np.arange(0,norm_gradient.shape[0]))
    # a=sampleImage(norm_gradient,X,Y) #samples au centre
    #...  
    
    # IMPLEMENTATION
    a = sampleImage(norm_gradient, X + direction_x, Y + direction_y)
    b = sampleImage(norm_gradient, X - direction_x, Y - direction_y)
		
    maxi = np.logical_and(norm_gradient >= a, norm_gradient >=b)*1
    return maxi 
 
def hysteresis(maxi,norm_gradient,seuil1,seuil2) :   
    # TODO: codez l'hysteresis (voir le cours )
    # 1) commencer par obtenir m1 et m2
    # 2) puis obtenez une image qui vaut 0 en dehors des bords et une valeur entière
    #    qui est constant sur chaque courbe connectée de m1 avec la fonction ndimage.label 
    #    (Attention: utilisez un voisinage 8 neighboorhood pour la fonction label...)
    #    ndimage.label reurn un tuple dont le premier élement est un tableau dans lequels
    #    les 1 du tableau donné en entré sont remplacés par un entier qui correspond
    #    au numéro de la courbe connectée
    # 3) utilisez la fonction ndimage.maximum  pour obtenir un vecteur dont la longeur 
    #    est le nombre de courbes conectée et dont le ieme element contient le maximum 
    #    que prend l'image m2 le long de la ieme courbe obtenue. le ieme element de ce 
    #    vecteur sera donc 
    #      - 1 s'il existe un pixel de la ieme courbe de m1 pourlequel m2 
    #        est 1 (c'est a dire dont le gradient est supérieur à seuil2)  
    #      - 0 sinon
    # 4) creez l'image edges en le fait que A[B] avec A un vecteur et B une matrice 
    #    à coefficient entiers donne une matrice C de même taille que B avec C[i,j]=A[B[i,j]] 
    #   (see http://docs.scipy.org/doc/numpy/user/basics.indexing.html#index-arrays in case 
    #    the index array is multidimensional)
    
    # IMPLEMENTATION
    # Etape 1)
    m1 = (norm_gradient > seuil1) * maxi
    m2 = (norm_gradient > seuil2) * maxi
    
    # Etape 2)

    s = [[1,1,1],
		[1,1,1],
		[1,1,1]]
    labels, labels_number = ndimage.label(m1, structure=s)  
    
    # Etape 3)
    bounds_exist_m2 = ndimage.maximum(m2, labels=labels, index=np.arange(1, labels_number + 1))
    
    # Etape 4)
    edges = np.hstack((0, bounds_exist_m2))[labels]
    
    return m1,m2,edges
    
def canny(im,sigma,seuil1,seuil2,display=True):
    
    im_smooth=smoothGaussian(im,sigma)
    
    gradient_x,gradient_y=gradient(im_smooth) 
    
    norm_gradient,angle=gradientNormeEtAngle(gradient_x,gradient_y)
    
    angle_rounded,direction_x,direction_y=approxAngleEtDirection(angle)
    
    maxi=localMaximum(norm_gradient,direction_x,direction_y)
    
    m1,m2,edges=hysteresis(maxi,norm_gradient,seuil1,seuil2)  

    '''
    with open('canny_etapes.pkl', 'wb') as f:
        l=[im_smooth.astype(np.float16),gradient_x.astype(np.float16),gradient_y.astype(np.float16),norm_gradient.astype(np.float16),angle.astype(np.float16),\
           angle_rounded.astype(np.float16),direction_x.astype(np.int8),direction_y.astype(np.int8),maxi,m1,m2,edges]
        pickle.dump(l,f)
    
    with open('canny_etapes.pkl', 'rb') as f:
        im_smooth,gradient_x,gradient_y,norm_gradient,angle,\
        angle_rounded,direction_x,direction_y,maxi,m1,m2,edges = pickle.load(f)
    '''
    
    if display: 
        plt.ion()
       
        plotImageWithColorBar(im_smooth,title='im_smooth')
        pause()
        
        plotImageWithColorBar(gradient_x,title='gradient x')
        pause()
        plotImageWithColorBar(gradient_y,title='gradient x')
        pause()
        displayImageAndVectorField(im_smooth,gradient_x,gradient_y,10,'b')  
        pause()
        plotImageWithColorBar(norm_gradient,title='norm_gradient')
        pause()
        plotImageWithColorBar(angle,cmap=plt.cm.hsv,title='angle') 
        pause()
        plotImageWithColorBar(angle_rounded,cmap=plt.cm.hsv)
        pause()
        displayImageAndVectorField(im_smooth,direction_x,direction_y,15,'b')
        pause()
        plotImageWithColorBar(m1)
        pause()
        plotImageWithColorBar(m2)   
        pause()
        plotImageWithColorBar(edges) 
        pause()'''
		
           
    return edges

def main():
    im=ndimage.imread('einstein.jpg')
    sigma=5    
    edges=canny(im,sigma,seuil1=1,seuil2=4,display=True)

if __name__ == "__main__":
    main()
