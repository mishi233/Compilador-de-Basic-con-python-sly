import unittest
from basrender import DotRender, ContentExtractor
from basast import *
from basparse import *

class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.l = Lexer()
        cls.p = Parser()

    def test_renderLet(self):
        top = self.p.parse(self.l.tokenize('10 LET X = 1'))
        
        extractor = ContentExtractor()
        content_let = extractor.visit_Let(top.statements[0].stmt)
        self.assertEqual(content_let[0], "Let")
        self.assertEqual(content_let[1][0], 'Variable')
        self.assertEqual(content_let[2][0], 'Number')

    def test_renderRead(self):
        top = self.p.parse(self.l.tokenize('10 READ A'))
        
        extractor = ContentExtractor()
        content_let = extractor.visit_Read(top.statements[0].stmt)
        self.assertEqual(content_let[0], "Read")
        self.assertEqual(content_let[1][0], 'Variable')

    def test_renderRead2(self):
        top = self.p.parse(self.l.tokenize('10 READ A, B, C'))
        
        extractor = ContentExtractor()
        content_read = extractor.visit_Read(top.statements[0].stmt)
        self.assertEqual(content_read[0], "Read")
        self.assertEqual(len(content_read), 4)

    def test_renderData(self):
        top = self.p.parse(self.l.tokenize('10 DATA 10, 20, 30'))
        
        extractor = ContentExtractor()
        content_let = extractor.visit_Data(top.statements[0].stmt)
        self.assertEqual(content_let[0], "Data")
        self.assertEqual(content_let[1][0], 'Number')

    def test_renderData2(self):
        top = self.p.parse(self.l.tokenize('10 DATA 10, 20, 30'))
        
        extractor = ContentExtractor()
        content_data = extractor.visit_Data(top.statements[0].stmt)
        self.assertEqual(content_data[0], "Data")
        self.assertEqual(len(content_data), 4)

    def test_renderPrint(self):
        top = self.p.parse(self.l.tokenize('10 PRINT "10"'))
        
        extractor = ContentExtractor()
        content_let = extractor.visit_Print(top.statements[0].stmt)
        self.assertEqual(content_let[0], "Print")
        self.assertEqual(content_let[1][0], 'String')
    
    def test_renderPrint2(self):
        top = self.p.parse(self.l.tokenize('10 PRINT "Hello", "World"'))
        
        extractor = ContentExtractor()
        content_print = extractor.visit_Print(top.statements[0].stmt)
        self.assertEqual(content_print[0], "Print")
        self.assertEqual(len(content_print), 3)

    def test_renderGoto(self):
        top = self.p.parse(self.l.tokenize('10 GOTO 100'))
        
        extractor = ContentExtractor()
        content_let = extractor.visit_Goto(top.statements[0].stmt)
        self.assertEqual(content_let[0], "Goto")
        self.assertEqual(content_let[1], '100')
    
    def test_renderIf(self):
        top = self.p.parse(self.l.tokenize('0 IF X > 0 THEN 40'))

        extractor = ContentExtractor()
        content_let = extractor.visit_If(top.statements[0].stmt)
        self.assertEqual(content_let[0], "If")
        self.assertEqual(content_let[1][0], 'Logical')
        self.assertEqual(content_let[2][0], 'DiscreteNumbers')
    
    def test_renderFor(self):
        top = self.p.parse(self.l.tokenize('100 FOR I = 1 TO 10 STEP 2'))

        extractor = ContentExtractor()
        content_let = extractor.visit_For(top.statements[0].stmt)
        self.assertEqual(content_let[0], "For")
        self.assertEqual(content_let[1][0], 'Variable')
        self.assertEqual(content_let[2][0], 'Number')
        self.assertEqual(content_let[3][0], 'Number')
        self.assertEqual(content_let[4][0], 'Number')
    
    def test_renderNext(self):
        top = self.p.parse(self.l.tokenize('120 NEXT I'))

        extractor = ContentExtractor()
        content_let = extractor.visit_Next(top.statements[0].stmt)
        self.assertEqual(content_let[0], "Next")
        self.assertEqual(content_let[1][0], 'Variable')
        
    def test_renderEnd(self):
        top = self.p.parse(self.l.tokenize('150 END FNA'))

        extractor = ContentExtractor()
        content_let = extractor.visit_End(top.statements[0].stmt)
        self.assertEqual(content_let[0], "End")
    
    def test_renderStop(self):
        top = self.p.parse(self.l.tokenize('150 STOP'))

        extractor = ContentExtractor()
        content_let = extractor.visit_Stop(top.statements[0].stmt)
        self.assertEqual(content_let, "Stop")
    
    def test_renderGoSub(self):
        top = self.p.parse(self.l.tokenize('160 GOSUB 210'))

        extractor = ContentExtractor()
        content_let = extractor.visit_GoSub(top.statements[0].stmt)
        self.assertEqual(content_let[0], "GoSub")

    def test_renderDim(self):
        top = self.p.parse(self.l.tokenize('170 DIM A1(5)'))

        extractor = ContentExtractor()
        content_let = extractor.visit_Dim(top.statements[0].stmt)
        self.assertEqual(content_let[0], "Dim")
        self.assertEqual(content_let[1][0], "DimItem")
    

if __name__ == '__main__':
    unittest.main()