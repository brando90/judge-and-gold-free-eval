import json
DS = {
'deepscaler-7605':('MULTI','other','cos(pi+theta)=-1/2 gives theta=+-pi/3 (+2k pi); tan(theta-9pi)=sqrt3 or -sqrt3, no quadrant given'),
'deepscaler-8179':('MULTI','ambiguous_reading','borderline: equal split over minimal 12 CDs -> 69.75; equal split over 13 CDs -> 64.38 also fits "up to 75"; filling -> 75'),
'deepscaler-12237':('MULTI','ambiguous_reading','broken chair position unspecified: end chair -> 7/9 (ref), interior chair -> 29/36'),
'deepscaler-23406':('MULTI','ambiguous_reading','borderline: population SD sqrt(2) (ref) vs sample SD with n-1 sqrt(5/2)'),
'deepscaler-25643':('MULTI','open_choice','borderline: min area 8/5 attained for k=+-1, so "find the equation of line AB" has y=x and y=-x; ref gives the area'),
'deepscaler-30908':('MULTI','other','underdetermined: p(2f+200)=7500; f=50,p=25 -> 1250 (ref); f=25,p=30 -> 750; f=150,p=15 -> 2250'),
'deepscaler-31879':('MULTI','other','a.b=-x^2+2x+3=0 -> x=3 or x=-1; "find the value of x", ref -1 only'),
'deepscaler-865':('UNCLEAR',None,'figure missing (AMC grid)'),
'deepscaler-2532':('UNCLEAR',None,'answer choices missing ("then:")'),
'deepscaler-2653':('UNCLEAR',None,'variable symbols stripped; t-s vs s-t sign undetermined'),
'deepscaler-12476':('UNCLEAR',None,'"as shown" figure missing'),
'deepscaler-19877':('UNCLEAR',None,'diagram missing; 3x4 dots gives 18 axis-aligned rectangles, ref 60 matches 3x4 cells'),
'deepscaler-20325':('UNCLEAR',None,'B_1 undefined (likely O_1)'),
'deepscaler-21807':('UNCLEAR',None,'orientation of 2x3 rectangle unclear and ref 5/2 inconsistent with both'),
'deepscaler-25224':('UNCLEAR',None,'inconsistent data: orange = 160/6 not integer; ref 27'),
'deepscaler-26863':('UNCLEAR',None,'expression not scale invariant (deg 4/deg 6) so unbounded; malformed'),
'deepscaler-27893':('UNCLEAR',None,'natural reading gives width ~527 m, ref 16.38 cannot be reproduced; figure/setup missing'),
'deepscaler-29358':('UNCLEAR',None,'640=2^9+2^7 uniquely; "at least three distinct powers" impossible'),
'deepscaler-32065':('UNCLEAR',None,'with a+b+c=3 the expression is not constant (likely a+b+c=0)'),
'deepscaler-25638':('UNCLEAR',None,'ref 554400 matches neither labeled (997920) nor unlabeled VP (498960) counting'),
'deepscaler-9338':('UNIQUE',None,'multi-part; ref covers last part'),
'deepscaler-11103':('UNIQUE',None,'multi-part; ref 60 is price for max profit (part 3); part 2 answer 50'),
'deepscaler-14103':('UNIQUE',None,'numeric approximation with tolerance 0.01'),
'deepscaler-14448':('UNIQUE',None,'python check: only one equilateral configuration, EF=4sqrt3'),
'deepscaler-31229':('UNIQUE',None,'"find all integers A": set is {18,-18}; ref incomplete but set unique'),
'deepscaler-28578':('UNIQUE',None,'two-part; ref gives max |A|=16'),
'deepscaler-20777':('UNIQUE',None,'frequency = count 30 (relative frequency 0.3 is a different quantity name)'),
'deepscaler-26537':('UNIQUE',None,'joint probability 0.665 natural reading'),
'deepscaler-29528':('UNIQUE',None,'ref appears wrong but unique'),
}
NQ_MULTI = {
4:('temporal','"last year" unfixed: South Carolina (2017), Notre Dame (2018), UConn (2016)'),
165:('ambiguous_reading','White Witch: Tilda Swinton (2005 film) vs Barbara Kellerman (1988 BBC series)'),
254:('multiple_entities','Hindi and Bengali (and English) each a most-spoken language'),
255:('multiple_entities','three hyenas: Shenzi, Banzai, Ed'),
257:('ambiguous_reading','official name Kingdom of Saudi Arabia vs former name Kingdom of Hejaz and Nejd'),
472:('temporal','142,907 (2016 census) vs 154,331 (2021 census)'),
533:('temporal','next episode date depends on when asked'),
572:('multiple_entities','calf muscles: gastrocnemius and soleus'),
599:('multiple_entities','any album track: Old Dan Tucker, Jesse James'),
612:('ambiguous_reading','since 1988 (Larry Shaw) vs 2009 (US House resolution)'),
698:('ambiguous_reading','location unspecified: gold has 1990 and 1995 bans'),
837:('temporal','Eagles won Super Bowl LII (2017 season) and LIX (2024 season)'),
894:('multiple_entities','Cory, Kory'),
903:('ambiguous_reading','city proper (Chongqing/Shanghai/Beijing) vs metro (Tokyo/Delhi/Shanghai)'),
977:('multiple_entities','role theory and identity theory'),
1060:('temporal','6 seasons before 2020 revival, 7 after'),
1065:('temporal','return date depends on season'),
1066:('ambiguous_reading','UK 1983 vs US 1984'),
1110:('ambiguous_reading','27 ratified vs 33 proposed by Congress'),
1127:('multiple_entities','Frankie Valli original; Andy Williams / Lauryn Hill / Boys Town Gang hit versions'),
1154:('temporal','Michael Schumacher (91) until 2020, Lewis Hamilton since'),
1234:('temporal','NBC, CBS, Fox in different seasons'),
1295:('temporal','2013 vs 2020'),
1298:('ambiguous_reading','Martin Lawrence (disguised) vs Ella Mitchell (actual Big Momma)'),
1352:('temporal','14 aired at the time vs 24 total'),
1373:('temporal','release date depends on when asked'),
1658:('ambiguous_reading','1983 (Ninety/One Ten) vs 1991 (named Defender)'),
1717:('temporal','11 at the time, more since'),
1834:('multiple_entities','Humboldt County, Del Norte County'),
2094:('ambiguous_reading','quantitative/qualitative vs experimental/correlational'),
2135:('temporal','Fallout (2018), Dead Reckoning (2023), The Final Reckoning (2025)'),
2137:('multiple_entities','The Royalettes (1965) vs Deniece Williams (1982 hit)'),
2181:('ambiguous_reading','Radcliffe Line vs International Border'),
2188:('multiple_entities','Idina Menzel (original Elphaba) vs Rachel Tucker'),
2224:('ambiguous_reading','origin (South America/Brazil) vs top producers (Costa Rica, Philippines)'),
2257:('multiple_entities','Shia LaBeouf, Christy Carlson Romano'),
2350:('multiple_entities','several first-round sites that year, and year unspecified'),
2465:('ambiguous_reading','season unspecified: Chandan Shetty (S5) vs Pratham (S4)'),
2502:('multiple_entities','John F. Kennedy, Gerald Ford (Eagle Scout)'),
2506:('temporal','2012 vs 2017 vs later eruptions'),
2509:('multiple_entities','open list: lumber, carbon sink'),
2597:('ambiguous_reading','reopen closed tab (browsers) vs new tab (some apps)'),
2689:('temporal','2018 vs later wins'),
2783:('ambiguous_reading','steamship prefix vs US Navy hull code for submarine'),
2801:('temporal','2012-13 vs later seasons'),
2889:('ambiguous_reading','Cristiano Ronaldo (~311) vs Ronaldo Nazario (~104)'),
2947:('ambiguous_reading','tortoise vs Greenland shark vs ocean quahog'),
3215:('temporal','Action Jackson (2014) vs Bhuj (2021)'),
3254:('temporal','ranking changes yearly'),
3318:('temporal','depends on when asked'),
3324:('ambiguous_reading','1864 (bronze) vs 1943 (zinc-coated steel) vs 1982 (copper-plated zinc)'),
3364:('temporal','"this year" unfixed'),
3391:('temporal','Osceola County Stadium (to 2016) vs West Palm Beach (2017+)'),
3431:('ambiguous_reading','Glenn Close (1996) vs Betty Lou Gerson (1961 animated voice)'),
3458:('ambiguous_reading','reinstated 1978 and again 1984'),
3479:('temporal','return date depends on season'),
3483:('ambiguous_reading','Oct 14 2016 (first half) vs Jan 19 2018 (second half)'),
3591:('multiple_entities','any 2018 inductee: Ray Lewis, Randy Moss'),
}
NQ_UNCLEAR = {446:'record depends on era/definition; gold Tim Duncan doubtful',995:'malformed; gold six|two inconsistent',1523:'version unspecified, unsure of gold',2415:'no story specified',3450:'garbled: Stephanie vs Steffy Forrester'}
NQ_NOTE = {373:'co-writer set is one answer',511:'gold 2004 appears wrong (Sojourner 1997)',1845:'office (Governor) is the answer',3503:'survivor set is one answer',1310:'merengue is the national rhythm',2996:'set of aqueducts is one answer',3380:'set of states is one answer'}
def write(ds, fn):
    with open(f'pass1/labels_pass1_{ds}.jsonl','w') as f:
        for l in open(f'items_{ds}.jsonl'):
            d=json.loads(l); lab,st,j=fn(d['id']); f.write(json.dumps({'id':d['id'],'label':lab,'subtype':st,'justification':j})+'\n')
write('deepscaler', lambda i: DS.get(i,('UNIQUE',None,'')))
def nq(i):
    n=int(i.split('-')[1])
    if n in NQ_MULTI: return ('MULTI',)+NQ_MULTI[n]
    if n in NQ_UNCLEAR: return ('UNCLEAR',None,NQ_UNCLEAR[n])
    return ('UNIQUE',None,NQ_NOTE.get(n,''))
write('nqopen', nq)
import collections
for ds in ['math500','gsm8k','deepscaler','nqopen']:
    print(ds, collections.Counter(json.loads(l)['label'] for l in open(f'pass1/labels_pass1_{ds}.jsonl')))
