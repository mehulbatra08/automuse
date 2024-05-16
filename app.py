from flask import Flask, render_template, request
import pandas as pd
import textdistance
import re
from collections import Counter

app = Flask(__name__)

words = []

with open('autosuggestion/autocorrect book.txt', encoding='utf-8', mode='r') as f:
    data = f.read()
    data = data.lower()
    word = re.findall(r'\w+', data)
    words += word

unique_words = set(words)

word_frequency_dict = Counter(words)

total_words_frequency = sum(word_frequency_dict.values())
probs = {}

for k in word_frequency_dict.keys():
    probs[k] = word_frequency_dict[k] / total_words_frequency

def autocorrect(word):
    word = word.lower()
    if word in probs:
        print("The word is already there", word)
    else:
        similarities = [1 - (textdistance.jaccard.distance(w, word)) for w in word_frequency_dict.keys()]
        df = pd.DataFrame.from_dict(probs, orient='index').reset_index()
        df = df.rename(columns={'index': 'Word', 0: 'Probability'})
        df['Similarity'] = similarities
        output = df.sort_values(['Similarity', 'Probability'], ascending=False).head(10)
        return output.to_dict('records')

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/suggest', methods=['POST'])
def suggest():
    keyword = request.form['keyword'].lower()
    if keyword:
        suggestions = autocorrect(keyword)
        return render_template('index.html', suggestions=suggestions)

if __name__ == '__main__':
    app.run(debug=True)
