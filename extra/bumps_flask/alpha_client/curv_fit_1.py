import bumps
from bumps.names import *

def line (x, m, b=0):
    return (m*x + b)

x = [1,2,3,4,5,6]
y = [2.1,4.1,6.3,8.03,9.6,11.9]
dy = [0.2,0.2,0.2,0.2,0.2,0.2]

M = Curve(line,x,y,dy,m=2,b=2)

M.m.range(0,4)
M.b.range(-5,5)

problem = FitProblem(M)

