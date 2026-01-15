import os
from lxml import html
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd

# Ensure VADER is ready
nltk.download('vader_lexicon')

def analyze_character_vibes(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        tree = html.fromstring(f.read())

    sia = SentimentIntensityAnalyzer()
    
    # List of characters we want to analyze based on your TEI IDs
    characters = ["SCOTT", "LUCAS LEE", "RAMONA", "WALLACE"]
    results = []

    print(f"{'Character':<15} | {'Sentiment':<10} | {'Vibe'}")
    print("-" * 40)

    for char in characters:
        # Extract dialogue specifically for this speaker
        # Using XPath to find the speaker span and the immediately following dialogue span
        dialogues = tree.xpath(f"//span[@class='speaker' and text()='{char}']/following-sibling::span[@class='dialogue'][1]/text()")
        
        full_text = " ".join(dialogues)
        
        if full_text.strip():
            score = sia.polarity_scores(full_text)['compound']
            
            # Categorize the 'vibe'
            if score > 0.1: vibe = "Positive/Excited"
            elif score < -0.1: vibe = "Aggressive/Negative"
            else: vibe = "Neutral/Observational"
            
            results.append({"Character": char, "Score": score, "Vibe": vibe})
            print(f"{char:<15} | {score:>10.4f} | {vibe}")

    # Bonus: Action vs Dialogue Ratio
    all_dialogue = tree.xpath("//span[@class='dialogue']/text()")
    all_actions = tree.xpath("//span[@class='stage']/text()")
    
    diag_len = sum(len(d.split()) for d in all_dialogue)
    act_len = sum(len(a.split()) for a in all_actions)
    
    print("\n--- Scene Rhythm ---")
    print(f"Total Words in Dialogue: {diag_len}")
    print(f"Total Words in Action: {act_len}")
    print(f"Action Density: {(act_len / (diag_len + act_len)) * 100:.1f}%")

if __name__ == "__main__":
    target = os.path.join("fulltext", "scott_scene.html")
    if os.path.exists(target):
        analyze_character_vibes(target)
    else:
        print("Error: HTML file not found.")