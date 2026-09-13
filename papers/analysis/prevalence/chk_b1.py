import math, itertools, cmath
from math import comb
# 41
for th in [math.pi/3, -math.pi/3]:
    print('41', math.cos(math.pi+th), math.tan(th-9*math.pi))
# 47
print('47', 11*75+12, 12*69.75, math.ceil(837/75))
# 63
def p63(broken):
    seats=[i for i in range(10) if i!=broken]
    pairs=list(itertools.combinations(seats,2))
    adj=sum(1 for a,b in pairs if abs(a-b)==1)
    return 1-adj/len(pairs)
from fractions import Fraction
for br in [0,4]:
    seats=[i for i in range(10) if i!=br]
    pairs=list(itertools.combinations(seats,2))
    adj=sum(1 for a,b in pairs if abs(a-b)==1)
    print('63 broken',br, Fraction(len(pairs)-adj,len(pairs)))
# 65
for b in range(1,200):
    n=3*b; T=comb(n,2)
    if T%16: continue
    G=7*T//16; B=9*T//16
    if G>=comb(2*b,2) and B>=comb(b,2): print('65', n)
# 80: Jia Yi Bing Ding
sols=[]
for p in itertools.permutations([1,2,3,4]):
    J,Y,B,D=p
    ok=True
    for (s,t,claim) in [(J,Y,Y==4),(Y,B,B==3),(B,D,D==2),(D,J,J==1)]:
        same=(s%2==t%2)
        if same!=claim: ok=False
    if ok and J+D<Y+B: sols.append(p)
print('80',sols)
# 67
a,b,c=17**(1/3),67**(1/3),97**(1/3)
import numpy as np
e1=a+b+c; e2=a*b+b*c+c*a; e3=a*b*c
r=np.roots([1,-e1,e2,-(e3+0.5)])
print('67', sum(x**3 for x in r))
# 68
print('68', 808080/(202**3-4*202**2+2*202))
# 96
cnt=0
for s in itertools.combinations(range(1,7),3):
    pairs=sum(1 for x,y in itertools.combinations(s,2) if abs(x-y)==1)
    if pairs==1: cnt+=1
print('96',cnt,'/20')
# 98 max cos a
best=-2
N=2000
for i in range(N):
    A=2*math.pi*i/N
    # solve cos(A-B)-cosA+cosB=0 over B grid
    prev=None
    for j in range(N+1):
        Bv=2*math.pi*j/N
        v=math.cos(A-Bv)-math.cos(A)+math.cos(Bv)
        if prev is not None and prev*v<=0: best=max(best,math.cos(A))
        prev=v
print('98',best, math.sqrt(3)-1)
# 1: quadrilateral both configurations
def ang(P,Q,R):
    v1=(P[0]-Q[0],P[1]-Q[1]); v2=(R[0]-Q[0],R[1]-Q[1])
    return math.degrees(math.acos((v1[0]*v2[0]+v1[1]*v2[1])/math.hypot(*v1)/math.hypot(*v2)))
B=(0,0); C=(1,0)
for sa in [1,-1]:
    A=(math.cos(math.radians(70)), sa*math.sin(math.radians(70)))
    D=(1+math.cos(math.radians(10)), math.sin(math.radians(10)))
    print('1 side',sa, ang(B,A,D), 'ABC',ang(A,B,C),'BCD',ang(B,C,D))
