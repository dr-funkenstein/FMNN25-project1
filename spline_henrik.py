from scipy import *
from matplotlib import *
from pylab import *
import scipy.linalg as sl


class Spline(object):

    #TODO Interpolation stuff
    def __init__(self,ctrlP,knotP=None):
        '''
            Arguments:
                ctrlP: control points, (L x 2) matrix
                knotP: knot points, (L+4 x 1) matrix
                       default: equidistant on [0,1]
        '''
        self.ctrlP = ctrlP
        self.ncp = len(ctrlP)
        self.knotP = fixKnotPoints(self.ncp,knotP)

    def __call__(self,x):
        '''
           de-Boor algorithm to evaluate BSpline
           x:     point to evaluate
        '''

        # k: s.t. u[k]<x<u[k+1]
        # p: degree (smoothness)
        # s: multiplicity of point (TODO)
        # cp[j,r]: result of de-boor algorithm at step j,r
        #          TODO: no need for matrix, change to vector or something
        k = searchsorted(self.knotP,x)-1
        if k<3 or k>self.ncp-1: # TODO find correct region
            raise Exception
        p = 3
        h = p
        s = 0
        cp = zeros((k-s+1 - (k-p),h+1,2))
        cp[:,0] = self.ctrlP[k-p:k-s+1]
        for r in xrange(1,h+1):
            j=r # Nobody likes indices
            for i in xrange(k-p+r,k-s+1):
                # TODO 0/0
                a = (x - self.knotP[i])/(self.knotP[i+p-r+1]-self.knotP[i])
                cp[j,r]=(1-a)*cp[j-1,r-1] + a*cp[j,r-1]
                j=j+1
        return cp[-1,-1]

    def plot(self,points=200,region=None):
        '''
            Plots the spline together with control points
            points: number of points to evaluate in region
            region: region to evaluate
                    default: full region
        '''
        if region==None:
            # TODO what is the maximum region?
            region=[self.knotP[3]+0.0001,self.knotP[-4]-0.001]
        x = linspace(region[0],region[1],200)
        y = array([self(xi) for xi in x])
        plot(y[:,0],y[:,1],'--')
        hold(True)
        plot(self.ctrlP[:,0],self.ctrlP[:,1])
        show()


def interpolation(interP,knotP=None):
    """
        Interpolates the given points and returns an object of the Spline class 
            Arguments:
                interP: interpolation points, (L x 2) matrix
                knotP: knot points, (L+4 x 1) matrix
                    default: equidistant on [0,1]
    """
    nip=len(interP)
    ctrlP=zeros((nip,2))
    knotP=fixKnotPoints(nip, knotP)
    xi=(knotP[:-2]+knotP[1:-1]+knotP[2:])/3
    nMatrix=zeros((nip,nip))
    for i in xrange(nip):
        fun=basisFunction(i,knotP)
        for k in xrange(nip):
            nMatrix[i,k]=fun(xi[k],3)
    print nMatrix
    print knotP

    ctrlP[:,0]=sl.solve_banded((nip-4,nip-4),nMatrix,interP[:,0])
    ctrlP[:,1]=sl.solve_banded((nip-4,nip-4),nMatrix,interP[:,1])

    
    return Spline(ctrlP,knotP)
    
    
    
def basisFunction(index, knotP):
    """
        Evaluates the basis function N for j given the knot points and returns
        a function
        Arguments:
            index: index
            knotP: knot points, (L+4 x 1) matrix
                default: equidistant on [0,1]
    """
    
    def n(x, order):
        """
            Evaluates the basis function at x for a given order
            Arguments:
                x: point to evaluate
                order: the order of the spline
        """
        if order!=0:
            if knotP[index+order]-knotP[index]==0:
                den1=0
            else:
                den1=1/(knotP[index+order]-knotP[index])
            if knotP[index+order+1]-knotP[index+1]==0:
                den2=0
            else:
                den2=1/(knotP[index+order+1]-knotP[index+1])
            nj=(x-knotP[index])*den1*n(x,order-1)+(knotP[index+order+1]-x)*den2*basisFunction(index+1,knotP)(x,order-1)
        else:
            if knotP[index]==knotP[index+1]:
                return 0
            elif knotP[index]<=x<knotP[index+1]:
                return 1
            else:
                return 0
        return nj
    return n


def fixKnotPoints(ncp, knotP=None):
    """
        Fixes the dimension and sorts the knot points.
        Arguments:
            ncp: number of control points
            knotP: knot points, (L+4 x 1) matrix
                default: equidistant on [0,1]
    """
    # Check and set knot points
    # Equidistant on [0,1] by default
    if knotP == None:
        knotP = logspace(0,1,ncp-2)

    # Convert lists/tuples
    if not isinstance(knotP,ndarray):
        knotP = array(knotP)

    # Make sure it's sorted
    if not all(knotP[1:] >= knotP[:-1]):
        knotP = sort(knotP)

    # Verify shape
    # TODO be less restrictive about number of knot points  
    if shape(knotP) != (ncp+4,) and shape(knotP) != (ncp-2,) and shape(knotP) != (ncp,):
        raise NotImplemented
        
    # Fixes the lenght of the knot points 
    if shape(knotP) == (ncp-2,):
        newKnotP = zeros(ncp+4)
        newKnotP[:3] = array([knotP[0],knotP[0],knotP[0]])
        newKnotP[3:-3] = knotP
        newKnotP[-3:] = array([knotP[-1], knotP[-1],knotP[-1]])
        knotP = newKnotP
    elif shape(knotP) == (ncp,):
        newKnotP = zeros(ncp+4)
        newKnotP[:2] = array([knotP[0],knotP[0]])
        newKnotP[2:-2] = knotP
        newKnotP[-2:] = array([knotP[-1],knotP[-1]])
        knotP = newKnotP
    return knotP
        
# Some examples
def ex1():
    cp = array([ [0,0],[0,2],[2,3],[4,0],[6,3],[8,2],[8,0]])
    gp = array([0,0,1,1,1,2,2])
    s=Spline(cp)
    s.plot()

def ex2(k=12):
    cp = randn(k,2)
    gp = linspace(0,1,k+4)
    s = Spline(cp)
    s.plot()
    
def ex3():
    cp = array([ [0,0],[0,2],[2,3],[4,0],[6,3],[8,2],[8,0]])
    s=interpolation(cp)
    s.plot()
    plot(cp)