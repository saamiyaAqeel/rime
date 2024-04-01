
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
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense


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
        
        value = (illegal_activities_counter / len(input_array)) * 100
        chart = pieChart()

        print(len(input_array))
        print(chart.create_data_structure("Potential Illegal Activities", str(illegal_activities_counter)))

        return str(len(input_array)) ,chart.create_data_structure("Potential Illegal Activities", str(illegal_activities_counter))     
                  
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
            
     value = (argumentative_nature_counter / len(input_array)) * 100
     chart = pieChart()
     return str(len(input_array)), chart.create_data_structure("Potentially Argumentative Nature", str(argumentative_nature_counter))

    def strictKeywordSearch(self, keyword, passages):
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
    
     value = (total_occurrences / total_words) * 100
     chart = pieChart()
     return str(total_words), chart.create_data_structure("Strict Keyword Occurrences", str(total_occurrences))
    
    def get_synonyms(self, word):
     synonyms = []

     for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            synonyms.append(lemma.name())

     if not synonyms:
        return False

     return synonyms

    def rnn_sample(self):
     df = pd.read_csv('argumentativeNature.csv')

     texts = df['text'].values
     labels = df['label'].values

     tokenizer = Tokenizer()
     tokenizer.fit_on_texts(texts)
     word_index = tokenizer.word_index
     vocab_size = len(word_index) + 1

     sequences = tokenizer.texts_to_sequences(texts)

     max_sequence_length = max([len(seq) for seq in sequences])
     padded_sequences = pad_sequences(sequences, maxlen=max_sequence_length, padding='post')

     labels = np.array(labels)

     X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)

     embedding_dim = 16
     model = Sequential([
      Embedding(vocab_size, embedding_dim, input_length=max_sequence_length),
      LSTM(64),
      Dense(1, activation='sigmoid')
     ])

     model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
     print(model.summary())
     model.fit(X_train, y_train, epochs=20, verbose=2)
     loss, accuracy = model.evaluate(X_test, y_test)
     print(f'Accuracy: {accuracy*100:.2f}%')

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

        chart_data = chart.create_data_structure("Related Keyword Occurrences", str(occurrences))
        return str(total_words), synonyms, chart_data
    
     return False
    
