import unittest
from parser_engine.parser import parser1  # Import the Parser function from your Python code
from fixture_reader import load_fixture  # Replace 'fixture_reader' with the appropriate module

class TestParser(unittest.TestCase):
    def run_test(self, input_str, expected_output, expected_stress):
        output = []
        stress = []
        result = parser1(
            input_str,
            lambda value: (output.append(value), stress.append(0)),
            lambda value: (stress.__setitem__(-1, value) if stress else None)
        )
        self.assertNotEqual(result, False, 'Parser did not succeed')
        self.assertEqual(output, expected_output, 'Output mismatches')
        self.assertEqual(stress, expected_stress, 'Stress mismatches')

    def test_parser_with_fixtures(self):
        files = ['parser1-1.json']
        for file in files:
            test_data = load_fixture(file)
            for test in test_data:
                self.run_test(test['input'], test['output'], test['stress'])

if __name__ == '__main__':
    unittest.main()
