import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from pieChart import pieChart  
import pandas as pd


class TestPieChart(unittest.TestCase):
    
    def setUp(self):
        self.chart = pieChart()  

    def test_predict_illegal(self):
        inputs = ['A friend of mine got caught using counterfeit money at a concert', 'today is a beautiful day']
        final_array, total, structure = self.chart.predict_illegal(inputs)
        self.assertIn(inputs[0], final_array)
        self.assertEqual(structure['value'], '1')

    def test_predict_argumentative(self):
        inputs = ['today was horrible i hated every part of it it was lacking', 'today is a beautiful day']
        final_array, total, structure = self.chart.predict_argumentative_nature(inputs)
        self.assertIn(inputs[0], final_array)
        self.assertEqual(structure['value'], '1')
    
    def test_strict_keyword_search(self):
        keyword = "test"
        passages = ["This is a test", "This is another test", "test here", "no match here"]
        expected_total_words = 13  
        expected_occurrences = 3   
        total_words, data_structure = self.chart.strictKeywordSearch(keyword, passages)
        self.assertEqual(int(total_words), expected_total_words)
        self.assertEqual(data_structure['x'], "Strict Keyword Occurrences")
        self.assertEqual(data_structure['value'], str(expected_occurrences))
    
    def test_related_keywords(self):
        keyword = "hello"
        passages = ["hello there", "hi", "test here", "no match here"]
        expected_total_words = 8
        expected_occurrences = 2   
        relatedWords = ["hi", "hello"]
        length, synonyms, chart_data = self.chart.related_keyword_search(passages, keyword)
        self.assertEqual(int(length), expected_total_words)
        self.assertEqual(chart_data['x'], "Related Keyword Occurrences")
        self.assertEqual(chart_data['value'], str(expected_occurrences))
        self.assertEqual(synonyms, relatedWords)


    def test_create_data_structure(self):
        result = self.chart.create_data_structure("Test Label", "100")
        self.assertEqual(result, {'x': "Test Label", 'value': "100"})


if __name__ == '__main__':
    unittest.main()
