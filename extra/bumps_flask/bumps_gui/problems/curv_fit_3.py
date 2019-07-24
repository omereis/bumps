import bumps
from bumps.names import *

def line (x, m, b=0):
    return (m*x + b)

x  = [1,    2,    3,   4,    5,    6,    7,    8,    9,    10,   11,   12,   13,   14,   15,   16,   17,   18,   19,   20]    
y  = [2.2,  4.8,  6.0, 8.3,  10.7, 12.7, 14.9, 16.7, 18.9, 20.1, 22.6, 24.7, 26.7, 28.2, 30.6, 32.2, 34.2, 36.2, 38.9, 40.7]
dy = [0.05, 0.05, 0.2, 0.05, 0.2,  0.2,  0.05, 0.05, 0.2,  0.05, 0.2,  0.2,  0.05, 0.05, 0.2,  0.05, 0.2,  0.2,  0.05, 0.05]

M = Curve(line,x,y,dy,m=2,b=2)

M.m.range(0,4)
M.b.range(-5,5)

problem = FitProblem(M)

