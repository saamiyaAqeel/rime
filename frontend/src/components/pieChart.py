
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import csv
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from collections import Counter
from sklearn.svm import SVC
import nltk

class pieChart:
    nltk.download('wordnet')
    syn = ""

    def create_data_structure(self, label, numeric_value):
     data = {}
     data['x'] = label
     data['value'] = numeric_value
     return data
  
    def illegalActivities(self, input_array):
        X = []  
        y = []  

        with open("categories.csv", mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader: 
                if len(row) >= 2:
                    X.append(row[0])
                    y.append(row[1])
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=80)
        tfidf_vectorizer = TfidfVectorizer()
        X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = tfidf_vectorizer.transform(X_test)
        classifier = LogisticRegression()
        classifier.fit(X_train_tfidf, y_train)
        total_array_counter = 0
        illegal_activities_counter = 0

        for input_text in input_array:
            new_input_tfidf = tfidf_vectorizer.transform([input_text])
            predicted_intent = classifier.predict(new_input_tfidf)
            if("non" not in predicted_intent[0]):
               illegal_activities_counter += 1
        
        value = (illegal_activities_counter/len(input_array)) * 100
        chart = pieChart()

        return chart.create_data_structure("Potential Illegal Activities", str(value))     
                  
    def argumentativeNature(self, input_array):
     X = []  
     y = []  

     with open("argumentativeNature.csv", mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader: 
            if len(row) >= 2:
                X.append(row[0])
                y.append(row[1])
    
     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=80)

     tfidf_vectorizer = TfidfVectorizer()
     X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
     X_test_tfidf = tfidf_vectorizer.transform(X_test)

     classifier = SVC(kernel='linear')  
     classifier.fit(X_train_tfidf, y_train)
     argumentative_nature_counter = 0

     for input_text in input_array:
        new_input_tfidf = tfidf_vectorizer.transform([input_text])
        predicted_intent = classifier.predict(new_input_tfidf)
        if("1" in predicted_intent[0]):
           argumentative_nature_counter += 1
            
     value = (argumentative_nature_counter/len(input_array)) * 100
     chart = pieChart()
     return chart.create_data_structure("Potentially Argumentative Nature", str(value))

    def strictKeywordSearch(self,keyword, passages):
     total_occurrences = 0 
     total_words = 0
     keyword = keyword.lower().strip()
     
     for passage in passages:
        words = passage.strip().split()

        for word in words:
            word = word.lower().strip()
            total_words += 1
            if word == keyword:
                total_occurrences += 1
    
     
     value = (total_occurrences/total_words) * 100
     chart = pieChart()

     return chart.create_data_structure("Strict Keyword Occurences", str(value))
    
    # def get_synonyms(self, word):
    #   synonyms = set()

    #   for synset in wordnet.synsets(word):
    #     for lemma in synset.lemmas():
    #         synonyms.add(lemma.name())

    #   if (synonyms == set()):
    #      return False
      
    #   return synonyms
    def get_synonyms(self, word):
     synonyms = []

     for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            synonyms.append(lemma.name())

     if not synonyms:
        return False

     return synonyms


    def related_keyword_search(self, text, keyword):
     chart = pieChart()
     synonyms = chart.get_synonyms(keyword)

     if synonyms:
        print(synonyms)
        text_str = ' '.join(text)
        words = word_tokenize(text_str.lower())

        word_counter = Counter(words)
        occurrences = sum(word_counter[word] for word in synonyms)

        total_words = sum(len(passage.split()) for passage in text)
        value = (occurrences / total_words) * 100
        chart = pieChart()

        chart_data = chart.create_data_structure("Related Keyword Occurrences", str(value))
        print(chart_data)
        return synonyms, chart_data
    
     return False
    
    
# passage = "This is a sample passage where we will search for occurrences of related keywords."
# keyword = "Sample"
# chart_instance = pieChart()
# occurrences = chart_instance.related_keyword_search(passage, keyword)
# print("Number of occurrences of related keywords for '{}' in the passage: {}".format(keyword, occurrences))
# print(chart_instance.get_synonyms(keyword))

# # Example usage:
# input_array = ["I had such an amazing day yesterday, it was so good and wholesome", "today was horrible i hated every part of it, it was lacking."]
# chart_instance = pieChart()
# chart_instance.argumentativeNature(input_array)
