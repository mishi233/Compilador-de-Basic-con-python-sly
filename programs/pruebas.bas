10 DIM X1(11)
20 LET X1(0) = 0
30 LET X1(1) = 1 
40 LET X1(2) = 2 
50 LET X1(3) = 3 
60 LET X1(4) = 4 
70 LET X1(5) = 5 
80 LET X1(6) = 6 
90 LET X1(7) = 7 
100 LET X1(8) = 8 
110 LET X1(9) = 9 
120 LET X1(10) = 10
130 INPUT Y1
140 PRINT "TABLA DE " , Y1
150 FOR I = 0 TO 10
160   PRINT X1(I) , "x", Y1, "=", X1(I) * Y1
170 NEXT I
180 PRINT "HOLA"
190 GOTO 175
200 END