0 PRINT SIN(1)
10 READ A1, A2, A3, A4
15 LET D = A1 * A4 - A3 * A2
20 IF D = 0 THEN 65
30 READ B1, B2
37   LET X1 = (B1 * A4 - B2 * A2) / D
42   LET X2 = (A1 * B2 - A3 * B1) / D
55   PRINT X1, X2
60 GOTO 30
65 PRINT "NO UNIQUE SOLUTION"
70 DATA 1, 2, 4
80 DATA 2, -7, 5
85 DATA 1, 3, 4, -7
90 END