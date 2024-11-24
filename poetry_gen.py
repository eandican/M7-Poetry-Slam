import os
import json
import spacy
import random
import pronouncing
import numpy as np
import inflect
from glob import glob
from textblob import TextBlob
from language_tool_python import LanguageTool
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import KeyedVectors 
from flask import Flask, render_template, request, jsonify
"""

Title: InSpoet
Author: Emre Andican

Description: Limerick Generator that aims to create limericks based on
themes from a collection of over 1000 poets (specify which poet). Uses
TF-IDF scores and a template to generate limericks based on a specificed
poet from the user. Evaluates generated limericks through sentiment score
and total grammatical errors.

"""

# Initializes Flask app
app = Flask(__name__)

# Checker for saved poems
if not os.path.exists("prev_generated.json"):
    with open("prev_generated.json", "w") as f:
        f.write("[]") 


class Poem:
    """
    Class that represents each poem (inspiring set or generated)
    """
    def __init__(self, title, text):
        self.title = title
        self.text = text
        self.grammar_score = 0
        self.sentiment = 0
    
    def set_sentiment(self, score):
        self.sentiment = score

    def set_grammar(self, grammar):
        self.grammar_score = grammar


class InspiringSet:
    """
    Class that takes on every operation. Starts off by initializing 
    the word vectors in the 800mb GloVe file to help us find similar
    words. Then calls inflector to help mitigate the plurality 
    problem I was facing. End result is a limerick about one
    of our author's main themes (assumed through TF-IDF). Words are
    inserted through a template, and those words are sourced through
    pronouncing's rhymes library and GloVe embbedings (use GenSim to
    work with the embeddings)
    """
    def __init__(self, glove_path="glove.6B.50d.txt"):
        self.inspiring_poems = []
        self.nlp = spacy.load("en_core_web_sm")
        self.word_vectors = KeyedVectors.load_word2vec_format(
            glove_path, binary=False, no_header=True)
        self.inflector = inflect.engine()
    
    def conjugate(self, verb, tense='present', subject='it'):
        '''
        Use this to sort any conjugation issues. Not entirely sure I 
        handled the properties fully correctly, but takes into account
        some of the wild grammar/spelling issues I've seen over the course
        of this project.
        '''
        doc = self.nlp(verb)
        if not doc or len(doc) == 0:
            return verb 
        lemma = doc[0].lemma_
        irregular_verbs = {
            "be": {"past": "was", "present": "is"},
            "go": {"past": "went", "present": "goes"},
            "make": {"past": "made", "present": "makes"},
        }
        if lemma in irregular_verbs and tense in irregular_verbs[lemma]:
            return irregular_verbs[lemma][tense]
        if tense == 'present':
            if subject == 'it':
                return lemma + 's' if not lemma.endswith('s') else lemma
            return lemma   
        if tense == 'past':
            if lemma.endswith('y') and len(lemma) > 1 and not lemma[-2] in "aeiou": 
                return lemma[:-1] + 'ied'
            elif lemma.endswith('e'):
                return lemma + 'd'
            elif not lemma.endswith('ed'): 
                return lemma + 'ed'
        return lemma
    

    def generate_inspiring_poems(self, authors_poems):
        '''
        Function that helps find and extract the poems by the specified author
        '''
        author_folder = glob(f"{authors_poems}/*.json")

        for poem in author_folder:
            with open(poem, 'r', encoding='utf-8') as f:
                file_contents = json.load(f)
                title = file_contents.get('title')
                text = file_contents.get('text')
                extracted_poem = Poem(title, text)
                self.inspiring_poems.append(extracted_poem)


    def generate_nouns(self):
        '''
        Identifies nouns within the poems of the author
        '''
        nouns = []
        for poem in self.inspiring_poems:
            poem_text = " ".join(poem.text) if isinstance(
                poem.text, list) else poem.text
            for line in poem.text:
                doc = self.nlp(line)
                line_nouns = (
                    [token.text for token in doc if token.pos_ == "NOUN"])
                if line_nouns:
                    nouns.append(line_nouns)
        return nouns

    def handle_plurality(self, word, is_plural=True):
        '''
        Handles the plurality issues seen during limerick generations.
        '''
        if is_plural:
            return self.inflector.plural(word)
        return self.inflector.singular_noun(word) or word


    def generate_significant_nouns(self):
        '''
        Using concepts from class and Prof. Gomezgil's class to use tf-idf
        as a way to find the most significant nouns in each poem by author.
        Returns a dictionary with significant words (assume themes) for 
        each poem in their directory. 
        '''
        nouns = [" ".join(noun) for noun in self.generate_nouns()]

        vectorizer = TfidfVectorizer()

        noun_matrix = vectorizer.fit_transform(nouns)
        noun_features = vectorizer.get_feature_names_out()

        significant_nouns = {}
        for i, poem in enumerate(self.inspiring_poems):
            scores = noun_matrix[i].toarray().flatten()
        
            if np.any(scores):
                theme_noun = noun_features[scores.argmax()]
            else:
                theme_noun = "None"

            significant_nouns[poem.title] = theme_noun

        return significant_nouns


    def generate_similar(self, theme, n=13, pos=None):
        '''
        Utilizes GloVe to help find similar words to generate
        a limerick that makes more sense (as opposed to just
        sourcing words from the poems directly). Returns 13
        words
        '''
        if theme in self.word_vectors:
            related_words = self.word_vectors.most_similar(
                theme, topn=n)
            words = [word for word, _ in related_words]
            if pos is not None:
                return self.filter_words_by_pos(words, pos)
            return words
        return [theme]

    def filter_words_by_pos(self, words, pos):
        '''
        Helper for the GenSim function where we can filter words
        based on what were trying to find (nouns, adj, verbs, etc)
        '''
        filtered_words = []
        for word in words:
            doc = self.nlp(word)
            if doc and doc[0].pos_ == pos:
                filtered_words.append(word)
        return filtered_words


    def generate_limerick(self):
        '''
        Generates our limerick. Start off by locating significant nouns
        though our TF-IDF vectorizer. Chooses a random theme, then finds words
        related to the theme. Handles pularity/conjugation issues early, then
        finds rhymes. Words are inserted in a template (to the best of my
        understanding of the english language), attempting to follow a
        AABBA rhyme scheme that we see in limericks
        '''
        significant_nouns = list(
            self.generate_significant_nouns().values())
        significant_nouns = [
            word for word in significant_nouns if " " not in word and word.isalpha()]
        theme = random.choice(significant_nouns)

        related_nouns = self.generate_similar(theme, pos="NOUN")
        related_verbs = self.generate_similar(theme, pos="VERB")
        related_adjs = self.generate_similar(theme, pos="ADJ")

        if not related_nouns:
            related_nouns = ["sea", "moon", "tea", "sky", "sun"]

        if not related_verbs:
            related_verbs = ["gleam", "seek", "reek", "made", "slayed"]

        if not related_adjs:
            related_adjs = ["mysterious", "colorful", "bright"]

        adj1 = random.choice(related_adjs)
        adj2 = random.choice(related_adjs)
        adj3 = random.choice(related_adjs)

        noun1 = random.choice(related_nouns)
        noun1_singular = self.handle_plurality(noun1, is_plural=False)
        
        rhyme_b = pronouncing.rhymes(noun1_singular)
        if not rhyme_b:
            rhyme_b = [noun1_singular]

        verb1 = random.choice(related_verbs)
        updated_verb1 = self.conjugate(verb1, tense='present', subject='it')

        verb2 = random.choice(related_verbs)
        updated_verb2 = self.conjugate(verb2, tense='past')

        verb3 = random.choice(related_verbs)
        updated_verb3 = self.conjugate(verb3, tense='past')

        rhymes = pronouncing.rhymes(theme)
        if not rhymes:
            rhymes = [theme]

        limerick_lines = [ # Generic Template to place words in
            f"There once was a {adj1} {theme},",
            f"who {updated_verb1} by the {random.choice(rhymes)}.",
            f"But then came in a {adj2} {noun1_singular}.",
            f"They {updated_verb2} like a {adj3} {random.choice(rhyme_b)}.",
            f"Finally, it {updated_verb3} by the {random.choice(rhymes)}."
        ]

        title = f"Something about {theme}"

        return Poem(title, limerick_lines)


    def evaluate_grammar(self, poem):
        '''
        Helps evaluate the grammar issues within our limerick
        '''
        tool = LanguageTool('en-US')
        errors = 0
        
        for line in poem.text:
            matches = tool.check(line)
            errors += len(matches)

        poem.set_grammar(errors)
        return errors

    def evaluate_sentiment(self, poem):
        '''
        Helps evaluate the sentiment within our limerick. Finds
        this through dividing the overall sentiment by the amount
        of words it calculated it for.
        '''
        total_sentiment = 0
        count = 0

        for line in poem.text:
            blob = TextBlob(line)
            sentiment = blob.sentiment.polarity
            total_sentiment += sentiment
            if sentiment != 0.0:
                count += 1
        
        score = total_sentiment / count if count > 0 else 0
        poem.set_sentiment(score)
        return score


@app.route("/", methods=["GET"])
def index():
    '''
    Route for a our Flask app
    '''
    return render_template("index.html")


@app.route("/generate_limerick", methods=["POST"])
def generate_limerick():
    '''
    Allows us to generate poems on our server. Helps us fallback 
    to random author if user doesn't input properly. Also
    writes the poems into our JSON file
    '''
    try:
        data = request.get_json()
        author = data.get("author", "default_author").strip()

        print(f"Received author: {author}") # use to confirm author is right

        inspiring_set = InspiringSet()
        base_path = "collection/collection"
        author_folder = f"{base_path}/{author}"

        if not os.path.isdir(author_folder):  # in the event that user misspells
            print(f"Author '{author}' not found. Using a random author.")
            available_authors = [
                d for d in os.listdir(base_path) if os.path.isdir(f"{base_path}/{d}")]
            if available_authors:
                author = random.choice(available_authors)
                author_folder = f"{base_path}/{author}"
                print(f"Using random author: {author}")

        inspiring_set.generate_inspiring_poems(author_folder)
        limerick = inspiring_set.generate_limerick()

        print(f"Generated limerick: {limerick.text}") 

        response = {
            "title": limerick.title,
            "lines": limerick.text,
            "author": author,
            "grammar_score": inspiring_set.evaluate_grammar(limerick),
            "sentiment_score": inspiring_set.evaluate_sentiment(limerick),
        }

        with open("prev_generated.json", "r") as f:
            try:
                saved_poems = json.load(f)
            except json.JSONDecodeError:
                saved_poems = []

        saved_poem = {
            "id": random.randint(1000, 9999), 
            "author": author,
            "title": limerick.title,
            "lines": limerick.text,
            "grammar_score": response["grammar_score"],
            "sentiment_score": response["sentiment_score"],
        }
        saved_poems.append(saved_poem)

        with open("prev_generated.json", "w") as f:
            json.dump(saved_poems, f, indent=2) 

        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc() 
        return jsonify({"error": str(e)}), 500
    

@app.route("/show_saved", methods=["GET"])
def show_saved():
    '''
    Shows the previously generated limericks
    '''
    poems = []

    try:
        with open("prev_generated.json", "r") as f:
            poems = json.load(f)
            return jsonify(poems)
    except FileNotFoundError:
        return jsonify({"error": "Save some poems!!!"}), 404


if __name__ == "__main__":
    '''
    Using 5001 because I couldnt figure out how to stop
    5000 :)
    '''
    app.run(debug=True, port=5001)