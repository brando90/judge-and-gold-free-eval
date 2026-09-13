import math, itertools, random
from fractions import Fraction as F
print("7605: theta=+-pi/3 both satisfy cos(pi+theta)=-1/2")
for th in (math.pi/3, -math.pi/3):
    print("  cos(pi+th)=%.4f tan(th-9pi)=%.4f" % (math.cos(math.pi+th), math.tan(th-9*math.pi)))
print("31879: a.b=0 roots")
for x in (3,-1):
    a=(x-1,1,-x); b=(-x,3,-1); print("  x=%d dot=%d" % (x, sum(i*j for i,j in zip(a,b))))
print("30908: integer full price solutions p(2f+200)=7500")
for f in range(0,201):
    p=F(7500,2*f+200)
    if p.denominator==1 and (p/3)*(200-f)+p*f==2500:
        print("  f=%d p=%s third=%s full_rev=%s" % (f,p,p/3,p*f))
print("12237: broken chair position")
for k in range(1,11):
    usable=[c for c in range(1,11) if c!=k]
    pairs=list(itertools.combinations(usable,2)); adj=sum(1 for a,b in pairs if b-a==1)
    print("  broken=%d P(not adjacent)=%s" % (k, 1-F(adj,len(pairs))))
print("23406: sample 7,8,9,6,10 sd pop=%.4f (sqrt2=%.4f) sample(n-1)=%.4f" % (math.sqrt(sum((v-8)**2 for v in [7,8,9,6,10])/5), math.sqrt(2), math.sqrt(sum((v-8)**2 for v in [7,8,9,6,10])/4)))
print("25643: area^2=16(1+k^2)^2/((1+4k^2)(k^2+4)) at k=+-1:", [16*(1+k*k)**2/((1+4*k*k)*(k*k+4)) for k in (1,-1)], "(8/5)^2=",(8/5)**2, "min over grid", min(16*(1+k*k)**2/((1+4*k*k)*(k*k+4)) for k in [i/1000 for i in range(-5000,5001) if i!=0]))
print("14448: equilateral ECF, E on AB, F on AD")
s3=math.sqrt(3); C=(0,0); A=(12,0); B=(3,3*s3); D=(3,-3*s3)
def rot(p,ang): c,s=math.cos(ang),math.sin(ang); return (c*p[0]-s*p[1], s*p[0]+c*p[1])
for ang in (math.pi/3,-math.pi/3):
    # E = A + t(B-A); F=rot(E); need F on AD: F = A + u(D-A)
    best=None
    for i in range(0,100001):
        t=i/100000; E=(A[0]+t*(B[0]-A[0]), A[1]+t*(B[1]-A[1])); Fp=rot(E,ang)
        # distance of Fp from segment AD
        ux=(D[0]-A[0]); uy=(D[1]-A[1]); L=ux*ux+uy*uy
        u=((Fp[0]-A[0])*ux+(Fp[1]-A[1])*uy)/L
        if 0<=u<=1:
            d=math.hypot(Fp[0]-(A[0]+u*ux), Fp[1]-(A[1]+u*uy))
            if best is None or d<best[0]: best=(d,t,math.hypot(E[0]-Fp[0],E[1]-Fp[1]))
    print("  ang=%.2f best=%s (4sqrt3=%.4f)" % (ang,best,4*s3))
print("25638 org chart counts:")
from math import comb, perm
print("  VP labeled, managers unordered per VP:", 12*11*10*comb(9,2)*comb(7,2))
print("  VP unlabeled:", 12*comb(11,2)*comb(9,2)*comb(7,2))
print("  all 7 positions labeled:", perm(12,7), " ref 554400 / 12 =",554400/12, "554400/(12*11*10)=",554400/1320)
print("27893 tower: width if eye at 18m, near bank 45m, subtended 20deg:")
t1=math.atan(18/45); t2=t1-math.radians(20); print("  w=", 18/math.tan(t2)-45)
print("32065: a+b+c=3 expression values:")
def ex(a,b,c): return 1/(b*b+c*c-3*a*a)+1/(a*a+c*c-3*b*b)+1/(a*a+b*b-3*c*c)
for a,b in [(1,1.5),(2,0.3),(0.7,1.1)]:
    c=3-a-b; print("  ",a,b,c,ex(a,b,c))
print("26863: scale test f(t,t,t) =", [ (t*t*t*3*t)/((2*t)**3*(2*t)**3) for t in (1,0.1,0.01)])
print("29358: binary 640 =", bin(640))
print("8179: 837/12=",837/12," 837/13=",837/13)
