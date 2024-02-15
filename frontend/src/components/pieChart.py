# from sklearn.model_selection import train_test_split
# from sklearn.svm import SVC
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.model_selection import train_test_split
# from sklearn.svm import SVC
# import csv
# from sklearn.metrics import accuracy_score

# class pieChart:
  
#  def textClassifier(self, input_array):
#     X = []  
#     y = []  

#     # Read categories from CSV file
#     with open("frontend/src/components/categories.csv", mode='r', encoding='utf-8') as file:
#         csv_reader = csv.reader(file)
#         for row in csv_reader: 
#             if len(row) >= 2:
#                 X.append(row[0])
#                 y.append(row[1])
    
#     # Split data into train and test sets
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=80)

#     # Transform text data into TF-IDF features
#     tfidf_vectorizer = TfidfVectorizer()
#     X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)

#     # Train the classifier
#     classifier = SVC(kernel='linear', C=3.0)
#     classifier.fit(X_train_tfidf, y_train)

#     # Initialize counter for illegal activities
#     illegal_activities_count = 0

#     # Iterate over each input string
#     for input_text in input_array:
#         # Transform input text into TF-IDF features
#         new_messages_tfidf = tfidf_vectorizer.transform([input_text])
#         # Predict intent for the input text
#         predicted_intent = classifier.predict(new_messages_tfidf)
#         # Check if the predicted intent is "illegal activities"
#         print(predicted_intent)
#         if "illegal" in predicted_intent[0]:
#             illegal_activities_count += 1
        
#     return illegal_activities_count
#    # return "hello my name is "

# # Example usage:
# input_array = ["I had such an amazing day yesterday.", "Let's organize an illegal gambling event."]
# chart_instance = pieChart()
# count = chart_instance.textClassifier(input_array)
# print("Occurrences of 'illegal activities':", count)
  
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import accuracy_score
# import csv

# class pieChart:
  
#     def textClassifier(self, input_array):
#         X = []  
#         y = []  

#         # Read categories from CSV file
#         with open("frontend/src/components/categories.csv", mode='r', encoding='utf-8') as file:
#             csv_reader = csv.reader(file)
#             for row in csv_reader: 
#                 if len(row) >= 2:
#                     X.append(row[0])
#                     y.append(row[1])
        
#         # Split data into train and test sets
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=80)

#         # Convert text data into TF-IDF features
#         tfidf_vectorizer = TfidfVectorizer()
#         X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
#         X_test_tfidf = tfidf_vectorizer.transform(X_test)

#         # Train the classifier
#         classifier = LogisticRegression()
#         classifier.fit(X_train_tfidf, y_train)

#         # Make predictions on the test set
#         predictions = classifier.predict(X_test_tfidf)

#         # Evaluate the model
#         accuracy = accuracy_score(y_test, predictions)

#         print("Accuracy:", accuracy)

# # Example usage:
# input_array = ["I had such an amazing day yesterday.", "Let's organize an illegal gambling event."]
# chart_instance = pieChart()
# chart_instance.textClassifier(input_array)


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import csv

class pieChart:
  
    def textClassifier(self, input_array):
        X = []  
        y = []  

        # Read categories from CSV file
        with open("frontend/src/components/categories.csv", mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader: 
                if len(row) >= 2:
                    X.append(row[0])
                    y.append(row[1])
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=80)

        # Convert text data into TF-IDF features
        tfidf_vectorizer = TfidfVectorizer()
        X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
        X_test_tfidf = tfidf_vectorizer.transform(X_test)

        # Train the classifier
        classifier = LogisticRegression()
        classifier.fit(X_train_tfidf, y_train)

        # Iterate over each input string
        for input_text in input_array:
            # Transform input text into TF-IDF features
            new_input_tfidf = tfidf_vectorizer.transform([input_text])
            # Predict intent for the input text
            predicted_intent = classifier.predict(new_input_tfidf)
            print("Input:", input_text, "--> Prediction:", predicted_intent[0])

# Example usage:
input_array = ["I had such an amazing day yesterday, it was so good and wholesome", "Let's organize an illegal gambling event."]
chart_instance = pieChart()
chart_instance.textClassifier(input_array)
