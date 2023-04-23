import unittest
from unittest.mock import patch
from io import StringIO
from artemis import *

valid_voice_command = 'valid_command.wav'
invalid_voice_command = 'invalid_command.wav'


class TestArtemis(unittest.TestCase):

    def test_refine_phrase(self):
        print("Test: refine_phrase")
        phrase = "qual o maior planeta do sistema solar"
        action = "pesquisar"
        expected_output = "maior planeta sistema solar"
        self.assertEqual(refine_phrase(phrase, action), expected_output)

    def test_scrapperSummary(self):
        print("Test: scrapperSummary")
        search_terms = "maior planeta sistema solar"
        results = scrapperSummary(search_terms)
        self.assertTrue(len(results) > 0)

    def test_deepScrapper(self):
        print("Test: deepScrapper")
        search_terms = "maior planeta sistema solar"
        result = deepScrapper(search_terms)
        self.assertIsNotNone(result)

    def test_hasValidPrefix(self):
        print("Test: hasValidPrefix")
        text1 = "artemis, pesquisar maior planeta sistema solar"
        text2 = "ananda, pesquisar maior planeta sistema solar"
        self.assertTrue(hasValidPrefix(text1))
        self.assertFalse(hasValidPrefix(text2))

    def test_isTurnOffCommand(self):
        print("Test: isTurnOffCommand")
        text = "artemis, desligar"
        self.assertTrue(isTurnOffCommand(text))

    def test_hasValidKeyword(self):
        print("Test: hasValidKeyword")
        text = "artemis, pesquisar maior planeta sistema solar"
        self.assertTrue(hasValidKeyword(text))

    def test_hasValidAction(self):
        print("Test: hasValidAction")
        text = "artemis, pesquisar maior planeta sistema solar"
        self.assertTrue(hasValidAction(text))

    def test_executeAction(self):
        print("Test: executeAction")
        action = "pesquisar"
        search_terms = "maior planeta sistema solar"
        self.assertIsNone(executeAction(action, search_terms))

    def test_listen(self):
        print("Test: listen")
        audio = listen(valid_voice_command)
        self.assertIsNotNone(audio)


if __name__ == '__main__':
    unittest.main()
