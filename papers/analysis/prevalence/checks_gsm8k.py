print("gsm8k-93: Gerald old time", 38+2, "| ref reading time*0.9 =", 40*0.9, "| literal speed*1.1 -> time =", round(40/1.1,4))
print("gsm8k-187: simple =", 100*(1+0.02*3), "| monthly compound =", round(100*1.02**3,4))
left=60-60*2//3
print("gsm8k-306: left after morning =", left, "| ref: left split two ways ->", left/2, "| literal: half of left (", left/2, ") split two ways ->", left/2/2)
print("gsm8k-649: total reading 70*2000+20000 =", 70*2000+20000, "| additive reading 2000+70*2000+20000 =", 2000+70*2000+20000)
print("gsm8k-1254: cumulative 6*12-6*7 =", 6*12-6*7, "| concurrent 12-7 =", 12-7)
print("gsm8k-255 (UNCLEAR): 10 stalls ->", 8*(20+40//10), "| 20 stalls ->", 8*(20+40//20))
print("math500-385 (borderline UNIQUE): diff of exact", round(150/1.32-150/1.64,3), "| round each first", round(150/1.32)-round(150/1.64))
