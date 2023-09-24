import unittest
import json

from parser_engine.parse1 import parser1


def load_fixture(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestCase(unittest.TestCase):
    def test_parser1(self):
        output = []
        stress = []
        length = []

        def process_phoneme(value):
            output.append(value)
            stress.append(0)
            length.append(0)

        def process_stress(value):
            stress[-1] = value

        files = ["parser1-1.json"]
        for file in files:
            with self.subTest(file=file):
                tests = load_fixture(f'fixtures/{file}')
                for test in tests:
                    with self.subTest(input=test['input']):
                        output = []
                        stress = []
                        result = parser1(test['input'], process_phoneme, process_stress)
                        self.assertNotEqual(result, False, 'Parser did not succeed')
                        self.assertListEqual(output, test['output'], 'Output mismatches')
                        self.assertListEqual(stress, test['stress'], 'Stress mismatches')


if __name__ == '__main__':
    unittest.main()