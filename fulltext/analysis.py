import os
import string
from collections import Counter
from lxml import html
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer

# Download updated NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('vader_lexicon')

class TextAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_text = ""
        self.filtered_tokens = []

    def extract_and_tokenize(self):
        # Extract script content from the specific div
        with open(self.file_path, "r", encoding="utf-8") as f:
            tree = html.fromstring(f.read())
        
        self.raw_text = " ".join(tree.xpath('//div[@class="script-content"]//text()')).strip()
        
        # Tokenization and cleaning
        tokens = word_tokenize(self.raw_text.lower())
        stop_words = set(stopwords.words('english'))
        self.filtered_tokens = [w for w in tokens if w.isalnum() and w not in stop_words]

    def get_frequencies(self, top_n=10):
        # Display frequency distribution
        counts = Counter(self.filtered_tokens)
        print(f"\nTop {top_n} Keywords:")
        for word, count in counts.most_common(top_n):
            print(f"{word}: {count}")

    def run_sentiment(self):
        # Calculate sentiment polarity
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(self.raw_text)
        print(f"\nSentiment Scores: {scores}")

if __name__ == "__main__":
    # Pointing to the file inside the fulltext folder
    target_file = os.path.join("fulltext", "scott_scene.html")
    
    if os.path.exists(target_file):
        analyzer = TextAnalyzer(target_file)
        analyzer.extract_and_tokenize()
        analyzer.get_frequencies(10)
        analyzer.run_sentiment()
    else:
        print(f"Error: {target_file} not found.")