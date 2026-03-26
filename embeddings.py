import numpy as np
import pandas as pd
from Config import *
import random
seed =0
random.seed(seed)
np.random.seed(seed)

from sklearn.feature_extraction.text import TfidfVectorizer

def fit_vectorizer(df: pd.DataFrame):
    tfidfconverter = TfidfVectorizer(max_features=2000, min_df=4, max_df=0.90)
    data = df[Config.TICKET_SUMMARY] + ' ' + df[Config.INTERACTION_CONTENT]
    tfidfconverter.fit(data)
    return tfidfconverter

def transform_vectorizer(df: pd.DataFrame, vectorizer: TfidfVectorizer):
    data = df[Config.TICKET_SUMMARY] + ' ' + df[Config.INTERACTION_CONTENT]
    return vectorizer.transform(data).toarray()

def get_tfidf_features(df: pd.DataFrame, fit=False, vectorizer=None):
    if fit:
        vectorizer = fit_vectorizer(df)
    X = transform_vectorizer(df, vectorizer)
    return X, vectorizer

def combine_embd(X1, X2):
    return np.concatenate((X1, X2), axis=1)

