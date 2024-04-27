10 REM
20 REM     ELIZA/DOCTOR
30 REM     CREATED BY JOSEPH WEIZENBAUM
40 REM     THIS VERSION BY JEFF SHRAGER
50 REM     EDITIED AND MODIFIED FOR MITS 8K BASIC 4.0 BY STEVE NORTH
60 REM     CREATIVE COMPUTING PO BOX 789-M MORRISTOWN NJ 07960
70 REM
80 REM     -----INITIALIZATION-----
90 DIM C$(72),I$(72),K$(72),F$(72),S$(72),R$(72),P$(72),Z$(72)
100 DIM S(36),R(36),N(36)
110 LET N1=36:LET N2=12:LET N3=112
120 FOR X=1 TO N1+N2+N3:READ Z$:NEXT X:REM SAME AS RESTORE
130 FORX=1 TO N1
140 READ S(X),L:LET R(X)=S(X):LET N(X)=S(X)+L-1
150 NEXT X
160 PRINT "HI!  I'M ELIZA.  WHAT'S YOUR PROBLEM?"
170 REM
180 REM     -----USER INPUT SECTION-----
190 REM
200 INPUT I$
201 LET I$=" "+I$+"  "
210 REM  GET RID OF APOSTROPHES
220 FOR L=1 TO LEN(I$)
230 IFMID$(I$,L,1)="'"THENLETI$=LEFT$(I$,L-1)+RIGHT$(I$,LEN(I$)-L):GOTO230
240 IFL+4<=LEN(I$)THENIFMID$(I$,L,4)="SHUT"THENPRINT"SHUT UP...":END
250 NEXT L
255 IF I$=P$ THEN PRINT "PLEASE DON'T REPEAT YOURSELF!":GOTO 170
260 REM
270 REM     -----FIND KEYWORD IN I$-----
280 REM
290 RESTORE
295 LET S=0
300 FOR K=1 TO N1
310 READ K$
315 IF S>0 THEN360
320 FOR L=1 TO LEN(I$)-LEN(K$)+1
340 IF MID$(I$,L,LEN(K$))=K$THENLETS=K:LETT=L:LETF$=K$
350 NEXT L
360 NEXT K
365 IF S>0 THEN LETK=S:LETL=T:GOTO390
370 LETK=36:GOTO570:REM  WE DIDNT FIND ANY KEYWORDS
380 REM
390 REM     TAKE RIGHT PART OF STRING AND CONJUGATE IT
400 REM     USING THE LIST OF STRINGS TO BE SWAPPED
410 REM
420 RESTORE:FORX=1 TO N1:READ Z$:NEXT X:REM SKIP OVER KEYWORDS
430 LET C$=" "+RIGHT$(I$,LEN(I$)-LEN(F$)-L+1)
440 FOR X=1 TO N2/2
450 READ S$,R$
460 FOR L= 1 TO LEN(C$)
470 IF L+LEN(S$)>LEN(C$) THEN 510
480 IF MID$(C$,L,LEN(S$))<>S$ THEN 510
490 LET C$=LEFT$(C$,L-1)+R$+RIGHT$(C$,LEN(C$)-L-LEN(S$)+1)
495 LET L=L+LEN(R$)
500 GOTO 540
510 IF L+LEN(R$)>LEN(C$)THEN540
520 IF MID$(C$,L,LEN(R$))<>R$ THEN 540
530 LET C$=LEFT$(C$,L-1)+S$+RIGHT$(C$,LEN(C$)-L-LEN(R$)+1)
535 LET L=L+LEN(S$)
540 NEXT L
550 NEXT X
555 IF MID$(C$,2,1)=" "THENLETC$=RIGHT$(C$,LEN(C$)-1):REM ONLY 1 SPACE
560 REM
570 REM     NOW USING THE KEYWORD NUMBER (K) GET REPLY
580 REM
590 RESTORE:FOR X= 1 TO N1+N2:READ Z$:NEXT X
600 FORX=1TOR(K):READ F$:NEXT X:REM  READ RIGHT REPLY
610 LET R(K)=R(K)+1: IFR(K)>N(K) THEN LET R(K)=S(K)
620 IF RIGHT$(F$,1)<>"*" THEN PRINT F$:P$=I$:GOTO 170
630 PRINT LEFT$(F$,LEN(F$)-1);C$
640 LET P$=I$:GOTO 170
1000 REM
1010 REM     -----PROGRAM DATA FOLLOWS-----
1020 REM
1030 REM     KEYWORDS
1040 REM
1050 DATA "CAN YOU","CAN I","YOU ARE","YOURE","I DONT","I FEEL"
1060 DATA "WHY DONT YOU","WHY CANT I","ARE YOU","I CANT","I AM","IM "
1070 DATA "YOU ","I WANT","WHAT","HOW","WHO","WHERE","WHEN","WHY"
1080 DATA "NAME","CAUSE","SORRY","DREAM","HELLO","HI ","MAYBE"
1090 DATA " NO","YOUR","ALWAYS","THINK","ALIKE","YES","FRIEND"
1100 DATA "COMPUTER","NOKEYFOUND"
1200 REM
1210 REM     STRING DATA FOR CONJUGATIONS
1220 REM
1230 DATA " ARE "," AM ","WERE ","WAS "," YOU "," I ","YOUR ","MY "
1235 DATA " IVE "," YOUVE "," IM "," YOURE "
1300 REM
1310 REM     REPLIES
1320 REM
1330 DATA "DON'T YOU BELIEVE THAT I CAN*"
1340 DATA "PERHAPS YOU WOULD LIKE TO BE ABLE TO*"
1350 DATA "YOU WANT ME TO BE ABLE TO*"
1360 DATA "PERHAPS YOU DON'T WANT TO*"
1365 DATA "DO YOU WANT TO BE ABLE TO*"
1370 DATA "WHAT MAKES YOU THINK I AM*"
1380 DATA "DOES IT PLEASE YOU TO BELIEVE I AM*"
1390 DATA "PERHAPS YOU WOULD LIKE TO BE*"
1400 DATA "DO YOU SOMETIMES WISH YOU WERE*"
1410 DATA "DON'T YOU REALLY*"
1420 DATA "WHY DON'T YOU*"
1430 DATA "DO YOU WISH TO BE ABLE TO*"
1440 DATA "DOES THAT TROUBLE YOU?"
1450 DATA "TELL ME MORE ABOUT SUCH FEELINGS."
1460 DATA "DO YOU OFTEN FEEL*"
1470 DATA "DO YOU ENJOY FEELING*"
1480 DATA "DO YOU REALLY BELIEVE I DON'T*"
1490 DATA "PERHAPS IN GOOD TIME I WILL*"
1500 DATA "DO YOU WANT ME TO*"
1510 DATA "DO YOU THINK YOU SHOULD BE ABLE TO*"
1520 DATA "WHY CAN'T YOU*"
1530 DATA "WHY ARE YOU INTERESTED IN WHETHER OR NOT I AM*"
1540 DATA "WOULD YOU PREFER IF I WERE NOT*"
1550 DATA "PERHAPS IN YOUR FANTASIES I AM*"
1560 DATA "HOW DO YOU KNOW YOU CAN'T*"
1570 DATA "HAVE YOU TRIED?"
1580 DATA "PERHAPS YOU CAN NOW*"
1590 DATA "DID YOU COME TO ME BECAUSE YOU ARE*"
1600 DATA "HOW LONG HAVE YOU BEEN*"
1610 DATA "DO YOU BELIEVE IT IS NORMAL TO BE*"
1620 DATA "DO YOU ENJOY BEING*"
1630 DATA "WE WERE DISCUSSING YOU-- NOT ME."
1640 DATA "OH, I*"
1650 DATA "YOU'RE NOT REALLY TALKING ABOUT ME, ARE YOU?"
1660 DATA "WHAT WOULD IT MEAN TO YOU IF YOU GOT*"
1670 DATA "WHY DO YOU WANT*"
1680 DATA "SUPPOSE YOU SOON GOT*"
1690 DATA "WHAT IF YOU NEVER GOT*"
1700 DATA "I SOMETIMES ALSO WANT*"
1710 DATA "WHY DO YOU ASK?"
1720 DATA "DOES THAT QUESTION INTEREST YOU?"
1730 DATA "WHAT ANSWER WOULD PLEASE YOU THE MOST?"
1740 DATA "WHAT DO YOU THINK?"
1750 DATA "ARE SUCH QUESTIONS ON YOUR MIND OFTEN?"
1760 DATA "WHAT IS IT THAT YOU REALLY WANT TO KNOW?"
1770 DATA "HAVE YOU ASKED ANYONE ELSE?"
1780 DATA "HAVE YOU ASKED SUCH QUESTIONS BEFORE?"
1790 DATA "WHAT ELSE COMES TO MIND WHEN YOU ASK THAT?"
1800 DATA "NAMES DON'T INTEREST ME."
1810 DATA "I DON'T CARE ABOUT NAMES-- PLEASE GO ON."
1820 DATA "IS THAT THE REAL REASON?"
1830 DATA "DON'T ANY OTHER REASONS COME TO MIND?"
1840 DATA "DOES THAT REASON EXPLAIN ANYTHING ELSE?"
1850 DATA "WHAT OTHER REASONS MIGHT THERE BE?"
1860 DATA "PLEASE DON'T APOLOGIZE!"
1870 DATA "APOLOGIES ARE NOT NECESSARY."
1880 DATA "WHAT FEELINGS DO YOU HAVE WHEN YOU APOLOGIZE."
1890 DATA "DON'T BE SO DEFENSIVE!"
1900 DATA "WHAT DOES THAT DREAM SUGGEST TO YOU?"
1910 DATA "DO YOU DREAM OFTEN?"
1920 DATA "WHAT PERSONS APPEAR IN YOUR DREAMS?"
1930 DATA "ARE YOU DISTURBED BY YOUR DREAMS?"
1940 DATA "HOW DO YOU DO ... PLEASE STATE YOUR PROBLEM."
1950 DATA "YOU DON'T SEEM QUITE CERTAIN."
1960 DATA "WHY THE UNCERTAIN TONE?"
1970 DATA "CAN'T YOU BE MORE POSITIVE?"
1980 DATA "YOU AREN'T SURE?"
1990 DATA "DON'T YOU KNOW?"
2000 DATA "ARE YOU SAYING NO JUST TO BE NEGATIVE?"
2010 DATA "YOU ARE BEING A BIT NEGATIVE."
2020 DATA "WHY NOT?"
2030 DATA "ARE YOU SURE?"
2040 DATA "WHY NO?"
2050 DATA "WHY ARE YOU CONCERNED ABOUT MY*"
2060 DATA "WHAT ABOUT YOUR OWN*"
2070 DATA "CAN YOU THINK OF A SPECIFIC EXAMPLE?"
2080 DATA "WHEN?"
2090 DATA "WHAT ARE YOU THINKING OF?"
2100 DATA "REALLY, ALWAYS?"
2110 DATA "DO YOU REALLY THINK SO?"
2120 DATA "BUT YOU ARE NOT SURE YOU*"
2130 DATA "DO YOU DOUBT YOU*"
2140 DATA "IN WHAT WAY?"
2150 DATA "WHAT RESEMBLANCE DO YOU SEE?"
2160 DATA "WHAT DOES THE SIMILARITY SUGGEST TO YOU?"
2170 DATA "WHAT OTHER CONNECTIONS DO YOU SEE?"
2180 DATA "COULD THERE REALLY BE SOME CONNECTION?"
2190 DATA "HOW?"
2200 DATA "YOU SEEM QUITE POSITIVE."
2210 DATA "ARE YOU SURE?"
2220 DATA "I SEE."
2230 DATA "I UNDERSTAND."
2240 DATA "WHY DO YOU BRING UP THE TOPIC OF FRIENDS?"
2250 DATA "DO YOUR FRIENDS WORRY YOU?"
2260 DATA "DO YOUR FRIENDS PICK ON YOU?"
2270 DATA "ARE YOU SURE YOU HAVE ANY FRIENDS?"
2280 DATA "DO YOU IMPOSE ON YOUR FRIENDS?"
2290 DATA "PERHAPS YOUR LOVE FOR FRIENDS WORRIES YOU."
2300 DATA "DO COMPUTERS WORRY YOU?"
2310 DATA "ARE YOU TALKING ABOUT ME IN PARTICULAR?"
2320 DATA "ARE YOU FRIGHTENED BY MACHINES?"
2330 DATA "WHY DO YOU MENTION COMPUTERS?"
2340 DATA "WHAT DO YOU THINK MACHINES HAVE TO DO WITH YOUR PROBLEM?"
2350 DATA "DON'T YOU THINK COMPUTERS CAN HELP PEOPLE?"
2360 DATA "WHAT IS IT ABOUT MACHINES THAT WORRIES YOU?"
2370 DATA "SAY, DO YOU HAVE ANY PSYCHOLOGICAL PROBLEMS?"
2380 DATA "WHAT DOES THAT SUGGEST TO YOU?"
2390 DATA "I SEE."
2400 DATA "I'M NOT SURE I UNDERSTAND YOU FULLY."
2410 DATA "COME COME ELUCIDATE YOUR THOUGHTS."
2420 DATA "CAN YOU ELABORATE ON THAT?"
2430 DATA "THAT IS QUITE INTERESTING."
2500 REM
2510 REM     DATA FOR FINDING RIGHT REPLIES
2520 REM
2530 DATA 1,3,4,2,6,4,6,4,10,4,14,3,17,3,20,2,22,3,25,3
2540 DATA 28,4,28,4,32,3,35,5,40,9,40,9,40,9,40,9,40,9,40,9
2550 DATA 49,2,51,4,55,4,59,4,63,1,63,1,64,5,69,5,74,2,76,4
2560 DATA 80,3,83,7,90,3,93,6,99,7,106,6