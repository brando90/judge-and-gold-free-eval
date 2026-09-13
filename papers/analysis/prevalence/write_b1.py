import json
ids=[json.loads(l)['id'] for i,l in enumerate(open('items_deepscaler.jsonl')) if i<100]
special={
 1:("UNIQUE",None,"Standard reading (interior angle at C = 170, convex) gives 85; the alternative placement makes interior angle at C reflex (190), so not admissible."),
 2:("UNCLEAR",None,"Refers to a grid figure 'shown below' that is missing; segment lengths cannot be pinned without it."),
 3:("UNIQUE",None,"Answer choices missing but distance sqrt(72/17)~2.06 is determined; closest-to value within rounding tolerance."),
 10:("UNCLEAR",None,"Ends with 'then:' and missing answer choices; intended conclusion (a>1 vs solution interval for x) cannot be pinned."),
 12:("UNCLEAR",None,"Variable symbols stripped ('Let  be', 'What is ?'); cannot tell whether t-s (-13.5) or s-t (13.5) is asked."),
 28:("UNIQUE",None,"60/8 = 7.5; the division and its value are equivalent."),
 41:("MULTI","other","cos(pi+theta)=-1/2 gives cos theta=1/2 with sign of sin undetermined: theta=pi/3 gives tan=sqrt(3), theta=-pi/3 gives tan=-sqrt(3); both satisfy the condition (checked numerically)."),
 47:("MULTI","ambiguous_reading","Distribution unspecified: even split over 12 CDs gives 69.75 min each (12*69.75=837), while filling CDs gives 75 min on 11 CDs and 12 min on the last (11*75+12=837)."),
 57:("UNIQUE",None,"Multi-part; last-asked quantity (price at max profit) is 60; each sub-answer unique (part 2: x=50)."),
 60:("UNIQUE",None,"Multi-part; last part evaluates to 221/2."),
 63:("MULTI","ambiguous_reading","Position of broken chair unspecified: broken chair at an end gives 1-8/36=7/9; broken chair in the interior (e.g. 5th) gives 1-7/36=29/36 (brute-force checked)."),
 64:("UNIQUE",None,"Standard reading: binomial coefficient of 4th term largest => n=6, constant term 15/4."),
 66:("UNCLEAR",None,"Refers to squares positioned 'as shown' in a missing figure; configuration cannot be pinned."),
 67:("UNIQUE",None,"Unique value (computed 182.5; reference 181.5 appears wrong, not multi)."),
 68:("UNIQUE",None,"Unique y ~0.100015 (reference 1/10 is approximate)."),
 69:("UNIQUE",None,"168 shillings = 2016 pence = 8 pounds 8 shillings, equivalent units."),
 74:("UNIQUE",None,"Numeric approximation of ln 2 with 0.01 tolerance; values within tolerance treated as equivalent."),
 76:("UNIQUE",None,"Determinable without diagram (E = AC∩BD, F on BC): CF=60."),
 77:("UNIQUE",None,"Rotation argument shows only the symmetric equilateral triangle exists; EF=4sqrt3."),
 80:("UNIQUE",None,"Brute force: only 2341 satisfies all constraints."),
 88:("UNIQUE",None,"Major-axis vertex is collinear with foci, so vertex must be minor-axis vertex; e=1/2."),
 92:("UNIQUE",None,"Right angle at R or at P in PRS both give perimeter 22."),
 94:("UNIQUE",None,"Multi-part; last-asked quantity min cost 3660 (m=38) unique."),
 98:("UNIQUE",None,"Max of cos a is unique (numerically 1; reference >1 appears wrong, not multi)."),
 100:("UNIQUE",None,"sqrt(a)-b representation of sqrt(164)-8 is unique for naturals."),
 51:("UNIQUE",None,"Multi-part; last part value unique."),
 91:("UNIQUE",None,"Multi-part; last part value unique."),
 95:("UNIQUE",None,"Multi-part; cos A=3/5 forced (A<120), area unique."),
}
with open('labels_pass2_deepscaler_b1.jsonl','w') as f:
    for i,id_ in enumerate(ids,1):
        lab,sub,j=special.get(i,("UNIQUE",None,""))
        f.write(json.dumps({"id":id_,"label":lab,"subtype":sub,"justification":j})+"\n")
from collections import Counter
rows=[json.loads(l) for l in open('labels_pass2_deepscaler_b1.jsonl')]
print(len(rows), len(set(r['id'] for r in rows)), Counter(r['label'] for r in rows))
for r in rows:
    if r['label']!='UNIQUE': print(r['label'], r['id'])
