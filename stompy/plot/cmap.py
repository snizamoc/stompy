""" Various functions for loading gradients - specifically GMT *.cpt files, and Gimp *.ggr files
"""
from __future__ import print_function
import numpy as np

import colorsys
import os,glob

import ggr
import matplotlib.pyplot as plt
from matplotlib import colors

# these are the candidates for default in mpl1.5 / mpl2.0
# viridis is the new default
from mpl15 import magma,inferno,plasma,viridis


def list_gradients():
    """ Return the locally available colormaps
    """
    filenames = [os.path.basename(f) for f in glob.glob( os.path.join( os.path.dirname(__file__),"cmaps",'*') )
                 if f.endswith('.ggr') or f.endswith('.cpt')]

    return filenames

def write_sample():
    """ Write a plot with samples all of the gradients in list_gradients tiled onto a single
    plot
    """
    grads = list_gradients()

    rc('text', usetex=False)
    a=np.outer(np.arange(0,1,0.01),np.ones(10))
    plt.figure(figsize=(10,5))
    plt.subplots_adjust(top=0.8,bottom=0.05,left=0.01,right=0.99)
    
    maps=list_gradients()
      
    l=len(maps)+1
    for i, m in enumerate(maps):
        plt.subplot(1,l,i+1)
        plt.axis("off")
        plt.imshow(a,aspect='auto',cmap=load_gradient(m),origin="lower")
        plt.title(m,rotation=90,fontsize=10)
        
    plt.savefig(os.path.join( os.path.dirname(__file__), "cmaps","colormaps.png"),
                dpi=100,facecolor='gray')      
    

def load_gradient(filename,reverse=False):
    """ Choose which type of file this is based on the extension.
    """
    if filename.find('/') < 0:
        filename = os.path.join( os.path.dirname(__file__),"cmaps",filename)
          
    if filename.endswith('.ggr'):
        return ggr_cm(filename,reverse=reverse)
    else:
        return gmt_cm(filename,reverse=reverse)
    
def ggr_cm(filename,reverse=False):
    """ brute-force - evaluate the gradient at all 256 locations """
    grad = ggr.GimpGradient(filename)
    x = np.linspace(0,1,256)
    rgb = [ grad.color(xi) for xi in x]
    rgb_tuples = [ (r,g,b) for r,g,b in rgb]

    if reverse:
        rgb_tuples = list(rgb_tuples[::-1])

    return colors.LinearSegmentedColormap.from_list(os.path.basename(filename),rgb_tuples)

def cmap_transform(cmap,f):
    """ brute-force - evaluate the gradient at all 256 locations.
    f is a function [0,1] => [0,1], mapping the new values to 
    old.
    e.g. f=lambda x: (1-x)  would reverse a colormap
    """
    X = np.linspace(0,1,256)
    rgb_tuples = [ cmap(f(x)) for x in X]
    #rgb_tuples = [ (rgba,g,b) for rgba in rgb]

    return colors.LinearSegmentedColormap.from_list('transformed',rgb_tuples)

def cmap_reverse(cmap):
    return cmap_transform(cmap,lambda x: 1-x)

inferno_r=cmap_transform(inferno,lambda x: (1-x))
viridis_r=cmap_transform(viridis,lambda x: (1-x))
plasma_r=cmap_transform(plasma,lambda x: (1-x))
magma_r=cmap_transform(magma,lambda x: (1-x))
      
def gmt_cm(filename,reverse=False):
    cpt = gmtColormap(filename,reverse=reverse)
    return colors.LinearSegmentedColormap(os.path.basename(filename), cpt)

def gmtColormap(filename,reverse=False):
    try:
        f = open(filename)
    except:
        print("file %s not found"%filename)
        return None

    lines = f.readlines()
    f.close()

    x = []
    r = []
    g = []
    b = []
    colorModel = "RGB"
    for l in lines:
        ls = l.split()
        if l[0] == "#":
           if ls[-1] == "HSV":
               colorModel = "HSV"
               continue
           else:
               continue
        if ls[0] == "B" or ls[0] == "F" or ls[0] == "N":
           pass
        else:
            x.append(float(ls[0]))
            r.append(float(ls[1]))
            g.append(float(ls[2]))
            b.append(float(ls[3]))
            xtemp = float(ls[4])
            rtemp = float(ls[5])
            gtemp = float(ls[6])
            btemp = float(ls[7])

    x.append(xtemp)
    r.append(rtemp)
    g.append(gtemp)
    b.append(btemp)

    nTable = len(r)
    x = np.array( x , np.float64)
    r = np.array( r , np.float64)
    g = np.array( g , np.float64)
    b = np.array( b , np.float64)
    if colorModel == "HSV":
        for i in range(r.shape[0]):
            rr,gg,bb = colorsys.hsv_to_rgb(r[i]/360.,g[i],b[i])
            r[i] = rr ; g[i] = gg ; b[i] = bb
    if colorModel == "HSV":
        for i in range(r.shape[0]):
            rr,gg,bb = colorsys.hsv_to_rgb(r[i]/360.,g[i],b[i])
            r[i] = rr ; g[i] = gg ; b[i] = bb
    if colorModel == "RGB":
        r = r/255.
        g = g/255.
        b = b/255.
    xNorm = (x - x[0])/(x[-1] - x[0])

    red = []
    blue = []
    green = []

    ii = range(len(x))
    if reverse:
        ii = ii[::-1]

    for i in ii:
        xnorm = xNorm[i]
        if reverse:
            xnorm = 1-xnorm
                
        red.append(  [xnorm,r[i],r[i]])
        green.append([xnorm,g[i],g[i]])
        blue.append( [xnorm,b[i],b[i]])

    colorDict = {"red":red, "green":green, "blue":blue}
    return (colorDict)
  


def cmap_discretize(cmap, N):
    """Return a discrete colormap from the continuous colormap cmap.
    
        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.
    
    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)
    """
    if type(cmap) == str:
        cmap = get_cmap(cmap)
    colors_i = np.concatenate((linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N+1)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) for i in range(N+1) ]
    # Return colormap object.
    return colors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)


# use only a subset of a colormap:
def cmap_clip(cmap,low,high):
    """
    Return a sub-range of the given colormap
    low,high: normalized values for the range to return, [0,1]
    """
    if type(cmap) == str:
        cmap = get_cmap(cmap)

    if isinstance(cmap,matplotlib.colors.LinearSegmentedColormap):
        N = int( (high-low) * cmap.N )
    else:
        N = 256  # conservative overkill

    colors_i = np.concatenate( (linspace(float(low), float(high), N),[low]) )

    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N+1)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) for i in range(N+1) ]

    sub_cmap = colors.LinearSegmentedColormap(cmap.name + "_sub", cdict)
    # Return colormap object.
    return sub_cmap

