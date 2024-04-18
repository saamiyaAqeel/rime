 # This file is not used during the implementation of the project, but rather an isolation of the CNN created before integratio
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, Flatten, Dense, Dropout



def load_glove_embeddings(glove_file):
    embeddings_index = {}
    with open(glove_file, 'r', encoding='utf8') as f:
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
    return embeddings_index


def predict_argumentative_nature(input_array):
    glove_embeddings = load_glove_embeddings('glove.6B.50d.txt')

    df = pd.read_csv('argumentativeNature.csv')
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
    embedding_matrix = np.zeros((vocab_size, dim))
    for word, i in tokenizer.word_index.items():
     embedding_vector = glove_embeddings.get(word)
     if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector

    model = Sequential([
     Embedding(input_dim=vocab_size, output_dim=dim, embeddings_initializer=tf.keras.initializers.Constant(embedding_matrix), trainable=False),
     Conv1D(filters=64, kernel_size=2, activation='relu'),
     MaxPooling1D(pool_size=2),
     Flatten(),
     Dense(64, activation='relu'),
     Dropout(0.5),
     Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)

    model.fit(X_train, y_train, epochs=10, batch_size=8, verbose=1, validation_split=0.2)
    argumentative_nature_counter = 0

    for input_text in input_array:
        input_sequence = tokenizer.texts_to_sequences([input_text])
        padded_input_sequence = pad_sequences(input_sequence, maxlen=max_length, padding='post')
        prediction = model.predict(padded_input_sequence)
        if prediction > 0.4: 
            argumentative_nature_counter += 1

    percentage = (argumentative_nature_counter / len(input_array)) * 100

    return (percentage, 100 - percentage)

input_array = [
    "I think we should have stricter laws for environmental protection.",
    "Illegal dumping of waste should be heavily penalized.",
    "I love drugs and i want so many drugs"
    "Going for hikes in the mountains is so refreshing and peaceful.",
    "Why would anyone think it's okay to litter beautiful natural places?",
]

argumentative_percentage, non_argumentative_percentage = predict_argumentative_nature(input_array)
print(f"Argumentative: {argumentative_percentage}%, Non-Argumentative: {non_argumentative_percentage}%")


