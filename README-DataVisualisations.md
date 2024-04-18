# RIME Tool Setup Instructions

This document provides comprehensive setup instructions for both the frontend and backend components of the RIME data visualization tool. Please ensure to follow these steps carefully to successfully run the application.

Prior to reading this document please ensure you have followed the instructions on README.md or README-Windows.md to get the RIME application up and run before proceeding with the visualisations.

## Frontend Installation

1. **Node.js Dependencies:**
   To install the necessary Node.js dependencies for the frontend, navigate to your project's root directory and run:
   ```bash
   npm install
2. **Possible Front End Issues**
   If packages do not show as intended you can also install the dependencies seperately.
   ```bash
   npm install anychart-vue
   npm install anychart
   npm install vue-router
3. **Backend** In order to run the backend of the app, you must install these libraries before hand. 
    ```bash
    pip install Flask
    pip install Flask-CORS
    pip install tensorflow
    pip install numpy
    pip install pandas
    pip install matplotlib seaborn
    pip install scikit-learn
    pip install nltk
    import nltk
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
4. **Run Flask Server** To start the backend server, navigate to `\frontend\src\components` on another terminal to where RIME is running and run app.py. This might require replacing python with the specific command for your Python version, like python3: 
    ```bash 
    python app.py
### Now you have the data visualisations running on the browser.

5. **Running backend unit tests** To run the backend tests navigate to this directory `\frontend\src\components` and run the following command
   ```bash
   python -m unittest

