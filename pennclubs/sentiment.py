from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_comment_sentiment(comment_dict):

    for comment in comment_dict:
        vs = analyzer.polarity_scores(comment['content'])

        comment['sentiment_score'] = vs['compound']
    
    return comment_dict