
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import csv
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from collections import Counter
from sklearn.svm import SVC

class pieChart:

    def create_data_structure(self, label, numeric_value):
     data = {}
     data['x'] = label
     data['value'] = numeric_value
     return data
  
    def illegalActivities(self, input_array):
        X = []  
        y = []  
        # input_array = input_array.split(',')
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
                  
    # def argumentativeNature(self, input_array):
    #     X = []  
    #     y = []  

    #     # Read categories from CSV file
    #     with open("frontend/src/components/argumentativeNature.csv", mode='r', encoding='utf-8') as file:
    #         csv_reader = csv.reader(file)
    #         for row in csv_reader: 
    #             if len(row) >= 2:
    #                 X.append(row[0])
    #                 y.append(row[1])
        
    #     # Split data into train and test sets
    #     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=80)

    #     # Convert text data into TF-IDF features
    #     tfidf_vectorizer = TfidfVectorizer()
    #     X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
    #     X_test_tfidf = tfidf_vectorizer.transform(X_test)

    #     # Train the classifier
    #     classifier = LogisticRegression(max_iter=1000)
    #     classifier.fit(X_train_tfidf, y_train)

    #     # Iterate over each input string
    #     for input_text in input_array:
    #         # Transform input text into TF-IDF features
    #         new_input_tfidf = tfidf_vectorizer.transform([input_text])
    #         # Predict intent for the input text
    #         predicted_intent = classifier.predict(new_input_tfidf)
    #         print("Input:", input_text, "--> Prediction:", predicted_intent[0])

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
    
     for passage in passages:
        words = passage.split()  
        
        for word in words:
            if word == keyword:
                total_occurrences += 1

     total_words = sum(len(passage.split()) for passage in passages)
    
     value = (total_occurrences/total_words) * 100
     chart = pieChart()

     return chart.create_data_structure("Strict Keyword Occurences", str(value))
    
    def get_synonyms(self, word):
      synonyms = set()

      for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name())

      if (synonyms == set()):
         return False
      
      return synonyms

    def related_keyword_search(self,text, keyword):
     chart = pieChart()
     synonyms = chart.get_synonyms(keyword)

     if(synonyms != False):
       words = word_tokenize(text.lower())
       word_counter = Counter(words)
       occurrences = sum(word_counter[word] for word in synonyms)

       total_words = sum(len(passage.split()) for passage in text)
       value = (occurrences/total_words) * 100
       chart = pieChart()

       return chart.create_data_structure("Related Keyword Occurences", str(value))
     
     return False
    
# Example usage:
# passage = "This is a sample passage where we will search for occurrences of related keywords."
# keyword = "djsjksksk"
# chart_instance = pieChart()
# occurrences = chart_instance.related_keyword_search(passage, keyword)
# print("Number of occurrences of related keywords for '{}' in the passage: {}".format(keyword, occurrences))
# print(chart_instance.get_synonyms(keyword))

# # Example usage:
# input_array = ["I had such an amazing day yesterday, it was so good and wholesome", "today was horrible i hated every part of it, it was lacking."]
# chart_instance = pieChart()
# chart_instance.argumentativeNature(input_array)
