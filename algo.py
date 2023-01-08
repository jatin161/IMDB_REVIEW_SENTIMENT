import nltk

nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


# For Text data
def vader(text):
    # analyze the sentiment for the text
    scores = SentimentIntensityAnalyzer().polarity_scores(text)
    if scores['compound'] >= 0.05:
        return "Positive"

    elif scores['compound'] <= - 0.05:
        return "Negative"

    else:
        return "Neutral"


