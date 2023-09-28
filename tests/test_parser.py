import unittest
from parser_engine.parser import parser

class Test(unittest.TestCase):
    def test_parser(self):
        values = [
            'SAH5KSEHSFUHL',
            'PREHNTIHS',
            'AENIHZAAGAEMAXS',
            '/HEHLOW , MAY NEYM IHZ SAEM.',
            'IHZ KAORREHKT, PLEY5 AXGEH4N? AOR DUW YUW PRIY4FER PAONX?',
            'JAH5ST TEHSTIHNX',
            'WAH4N ZIY4ROW POYNT FAY4V PERSEH4NT',
            'WAH4N  TUW4  THRIY4  FOH4R  FAY4V  SIH4KS  ZIY4ROW POYNT FAY4V, AY4 KAEN KAWNT',
            'KAHMPYUWTER',
            '/HEHLOW',
            'WIHZAA5RD',
        ]

        for value in values:
            with self.subTest(value = value):
                result = parser(value)
                self.assertIsNot(result, False, 'Parser did not succeed')

if __name__ == '__main__':
    unittest.main()
