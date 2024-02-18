from textblob import TextBlob
from googletrans import Translator

def translate_to_english(text):
    translator = Translator()
    translated = translator.translate(text, src='ar', dest='en')
    return translated.text

def analyze_sentiment_arabic(text):
    english_text = translate_to_english(text)
    blob = TextBlob(english_text)
    sentiment = blob.sentiment.polarity
    return sentiment
def analyze_sentiment_score(score):
    if score > 0.3:
        return "Positive"
    elif score < -0.3:
        return "Negative"
    else:
        return "Neutral"
# Example usage
arabic_text = "تأخرت على موعد الاجتماع وأشعر بالإحباط الشديد"
sentiment_score = analyze_sentiment_arabic(arabic_text)
sentiment_category = analyze_sentiment_score(sentiment_score)
print("Sentiment category:", sentiment_category)
