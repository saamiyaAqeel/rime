
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
import random as python_random
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
import re
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, Flatten, Dense, Dropout, GlobalAveragePooling1D
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

class pieChart:
    nltk.download('wordnet')
    syn = ""

    # Method to load glove embeddings
    def load_glove_embeddings(self, glove_file):
     embeddings = {}
     with open(glove_file, 'r', encoding='utf8') as f:
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings[word] = coefs
     return embeddings
    
    # Method to plot confusion matrix
    def plotMatrix(self, true_labels, y_pred):
     cm = confusion_matrix(true_labels, y_pred)
     plt.figure(figsize=(9, 6))
     sns.heatmap(cm, annot=True, fmt="d", cmap='Blues', cbar=False, annot_kws={"size": 16})
     labels = np.array([['True Negatives: ' + str(cm[0, 0]), 'False Positives: ' + str(cm[0, 1])],
                       ['False Negatives: ' + str(cm[1, 0]), 'True Positives: ' + str(cm[1, 1])]])
     sns.heatmap(cm, annot=labels, fmt='', cmap='Blues', cbar=False, annot_kws={"size": 12, "weight": "bold", "color": "black", "ha": "center"}, alpha=0)
     plt.xlabel('Predicted Labels')
     plt.ylabel('True Labels')
     plt.title('Potential Argumentative')
     plt.show()

    # Method to load of evidenciary interest perctanges using a CNN 
    def predict_illegal(self, input_array):
     chart = pieChart()
     glove_embeddings = chart.load_glove_embeddings('glove.6B.50d.txt')

     df = pd.read_csv('illegalPotential.csv')
     df['text'] = df['text'].str.lower().str.replace(r'\W', ' ')
     texts = df['text'].tolist()
     labels = df['label'].tolist()

     tokenizer = Tokenizer()
     tokenizer.fit_on_texts(texts)
     vocab_size = len(tokenizer.word_index) + 1
     sequences = tokenizer.texts_to_sequences(texts)
     length = max([len(seq) for seq in sequences])
     padded_sequences = pad_sequences(sequences, maxlen=length, padding='post')
     labels = np.array(labels)

     dim = 50  
     embedding_matrix = np.zeros((vocab_size, dim))
     for w, i in tokenizer.word_index.items():
      embedding_vector = glove_embeddings.get(w)
      if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector

     model = Sequential([
      Embedding(input_dim=vocab_size, output_dim=dim, embeddings_initializer=tf.keras.initializers.Constant(embedding_matrix), trainable=False),
      Conv1D(128, 5, activation='relu'),
      MaxPooling1D(4),
      Conv1D(64, 5, activation='relu'),
      GlobalAveragePooling1D(),
      Dense(24, activation='relu'),
      Dropout(0.5),
      Dense(1, activation='sigmoid')
    ])

     model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
     model.summary()

     X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)
     model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test), verbose=2)

    # For confusion matrix diagrams 
    #  predictions = model.predict(X_test)
    #  predictions = (predictions > 0.5).astype(int)  
    #  chart.plotMatrix(y_test, predictions)

     illegal_activities_counter = 0
     text_array = []

     for input_text in input_array:
        input_sequence = tokenizer.texts_to_sequences([input_text])
        padded_input_sequence = pad_sequences(input_sequence, maxlen=length, padding='post')
        prediction = model.predict(padded_input_sequence)
        if prediction < 0.5:
            text_array.append(input_text)
            illegal_activities_counter += 1

     final_array = list(set(text_array))

     return final_array, str(len(input_array)), chart.create_data_structure("Of Evidenciary Interest", str(illegal_activities_counter))
    
    # Method for predicting argumentative nature using a CNN
    def predict_argumentative_nature(self, input_array):
     chart = pieChart()
     glove_embeddings = chart.load_glove_embeddings('glove.6B.50d.txt')

     df = pd.read_csv('argumentativeNature.csv')
     df['text'] = df['text'].str.lower().str.replace(r'\W', ' ')
     texts = df['text'].tolist()
     labels = df['label'].tolist()

     tokenizer = Tokenizer()
     tokenizer.fit_on_texts(texts)
     vocab_size = len(tokenizer.word_index) + 1
     sequences = tokenizer.texts_to_sequences(texts)
     max_length = max([len(seq) for seq in sequences])
     padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post')
     labels = np.array(labels)

     dim = 50  
     matrix = np.zeros((vocab_size, dim))
     for w, i in tokenizer.word_index.items():
      embedding_vector = glove_embeddings.get(w)
      if embedding_vector is not None:
        matrix[i] = embedding_vector

     model = Sequential([
      Embedding(input_dim=vocab_size, output_dim=dim, embeddings_initializer=tf.keras.initializers.Constant(matrix), trainable=False),
      Conv1D(128, 5, activation='relu'),
      MaxPooling1D(4),
      Conv1D(64, 5, activation='relu'),
      GlobalAveragePooling1D(),
      Dense(24, activation='relu'),
      Dropout(0.5),
      Dense(1, activation='sigmoid')
    ])

     model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
     model.summary()

     X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)
     model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test), verbose=2)

    # For confusion matrix diagrams 
    #  predictions = model.predict(X_test)
    #  predictions = (predictions > 0.5).astype(int)  
    #  chart.plotMatrix(y_test, predictions)
     
     argumentative_nature_counter = 0

     text_array = []

     for input_text in input_array:
        input_sequence = tokenizer.texts_to_sequences([input_text])
        padded_input_sequence = pad_sequences(input_sequence, maxlen=max_length, padding='post')
        prediction = model.predict(padded_input_sequence)
        if prediction > 0.5:
            text_array.append(input_text)
            argumentative_nature_counter += 1

     final_array = list(set(text_array))

     return final_array, str(len(input_array)), chart.create_data_structure("Potentially Argumentative Nature", str(argumentative_nature_counter))

    def create_data_structure(self, label, numeric_value):
     data = {}
     data['x'] = label
     data['value'] = numeric_value
     return data
    
    # Returns the amount of keywords present in a passage 
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
    
    # This method using wordnet to get synonyms of the keyword 
    def get_synonyms(self, word, text):
        text_tokens = set(word_tokenize(text.lower()))
        synonyms = set()

        for synset in wordnet.synsets(word):
            for lemma in synset.lemmas():
                lemma_name = lemma.name().replace('_', ' ')  
                if lemma_name in text_tokens:  
                    synonyms.add(lemma_name)

        if not synonyms:
            return False

        return list(synonyms)

    # Method for related keyword search, searches for the occurence of keyword and the synonyms using wordnet
    # If no words found, users are met with a no words found message
    def related_keyword_search(self, text, keyword):
        text_str = ' '.join(text)
        synonyms = self.get_synonyms(keyword, text_str)

        if synonyms:
            words = word_tokenize(text_str.lower())

            word_counter = Counter(words)
            occurrences = sum(word_counter[word] for word in synonyms)

            total_words = sum(len(passage.split()) for passage in text)
            value = (occurrences / total_words) * 100

            chart_data = self.create_data_structure("Related Keyword Occurrences", str(occurrences))
            return str(total_words), synonyms, chart_data
    
        return False

    # Logistic Regression Classifier that is not used anymore, was used in alpha phase implementation
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

        return str(len(input_array)) ,chart.create_data_structure("Potential Illegal Activities", str(illegal_activities_counter))     
                  
    # Logistic Regression Classifier that is not used anymore, was used in alpha phase implementation
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
    
     chart = pieChart()
     return str(len(input_array)), chart.create_data_structure("Potentially Argumentative Nature", str(argumentative_nature_counter))
