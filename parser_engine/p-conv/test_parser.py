import unittest
import json
from parser_code import parser


def load_fixture(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


class Test(unittest.TestCase):
    def test_parser1(self):
        files = ["parser1-1.json"]  # Replace with your file names
        for file in files:
            with self.subTest(file=file):
                tests = load_fixture(f'fixtures/{file}')
                for test in tests:
                    with self.subTest(input=test['input']):
                        output = []
                        stress = []
                        result = parser(test['input'])
                        self.assertNotEqual(result, False, 'Parser did not succeed')
                        self.assertListEqual(output, test['output'], 'Output mismatches')
                        self.assertListEqual(stress, test['stress'], 'Stress mismatches')


if __name__ == '__main__':
    unittest.main()


