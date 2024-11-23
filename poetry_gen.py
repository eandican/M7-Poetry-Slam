import textstat
import json
import spacy
import random
import pronouncing
import nltk
import numpy as np
from glob import glob
from textblob import TextBlob
from language_tool_python import LanguageTool
from sklearn.feature_extraction.text import TfidfVectorizer


class Poem:
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
    def __init__(self):
        self.inspiring_poems = []
        self.nlp = spacy.load("en_core_web_sm")

    def conjugate(self, verb, tense='present'):
        doc = self.nlp(verb)
        token = doc[0]
        if tense == 'present':
            return token.lemma_
        elif tense == 'past':
            return token.lemma_ + 'ed' 
        return verb

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
            poem_text = " ".join(poem.text) if isinstance(poem.text, list) else poem.text
            for line in poem.text:
                doc = self.nlp(line)
                line_nouns = ([token.text for token in doc if token.pos_ == "NOUN"])
                if line_nouns:
                    nouns.append(line_nouns)
        return nouns

    def generate_verbs(self):
        '''
        Identifies verbs within the poems of the author
        '''
        verbs = []
        for poem in self.inspiring_poems:
            poem_text = " ".join(poem.text) if isinstance(poem.text, list) else poem.text
            for line in poem.text:
                doc = self.nlp(line)
                line_verbs = ([token.text for token in doc if token.pos_ == "VERB"])
                if line_verbs:
                    verbs.append(line_verbs)
        return verbs

    def generate_adjectives(self):
        '''
        Identifies adjectives within the poems of the author
        '''
        adjectives = []
        for poem in self.inspiring_poems:
            poem_text = " ".join(poem.text) if isinstance(poem.text, list) else poem.text
            for line in poem.text:
                doc = self.nlp(line)
                line_adjs = ([token.text for token in doc if token.pos_ == "ADJ"])
                if line_adjs:
                    adjectives.append(line_adjs)
        return adjectives


    def generate_significant_nouns(self):
        '''
        Using concepts from class and Prof. Gomezgil's class to use tf-idf
        as a way to find the most significant nouns in each poem by author.
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


    def generate_significant_verbs(self):
        '''
        Using concepts from class and Prof. Gomezgil's class to use tf-idf
        as a way to find the most significant verbs in each poem by author.
        '''
        verbs = [" ".join(verb) for verb in self.generate_verbs()]

        vectorizer = TfidfVectorizer()

        verb_matrix = vectorizer.fit_transform(verbs)
        verb_features = vectorizer.get_feature_names_out()

        significant_verbs = {}
        for i, poem in enumerate(self.inspiring_poems):
            scores = verb_matrix[i].toarray().flatten()
        
            if np.any(scores):
                theme_verb = verb_features[scores.argmax()]
            else:
                theme_verb = "None"

            significant_verbs[poem.title] = theme_verb
        
        return significant_verbs


    def generate_significant_adjectives(self):
        '''
        Using concepts from class and Prof. Gomezgil's class to use tf-idf
        as a way to find the most significant adjectives in each poem by author.
        '''
        adjectives = [" ".join(adj) for adj in self.generate_adjectives()]

        vectorizer = TfidfVectorizer()

        adj_matrix = vectorizer.fit_transform(adjectives)
        adj_features = vectorizer.get_feature_names_out()

        significant_adjs = {}
        for i, poem in enumerate(self.inspiring_poems):
            scores = adj_matrix[i].toarray().flatten()
        
            if np.any(scores):
                theme_adj = adj_features[scores.argmax()]
            else:
                theme_adj = "None"

            significant_adjs[poem.title] = theme_adj
        
        return significant_adjs


    def generate_limerick(self):
        significant_nouns = list(self.generate_significant_nouns().values())
        significant_verbs = list(self.generate_significant_verbs().values())
        significant_adjs = list(self.generate_significant_adjectives().values())

        significant_nouns = [word for word in significant_nouns if " " not in word and word.isalpha()]
        significant_verbs = [word for word in significant_verbs if " " not in word and word.isalpha()]
        significant_adjs = [word for word in significant_adjs if " " not in word and word.isalpha()]

        theme = random.choice(significant_nouns)

        rhymes = pronouncing.rhymes(theme)
        if not rhymes:
            rhymes = [theme]

        noun1 = random.choice(significant_nouns)
        verb1 = random.choice(significant_verbs)
        verb2 = random.choice(significant_verbs)
        adj1 = random.choice(significant_adjs)
        adj2 = random.choice(significant_adjs)
        adj3 = random.choice(significant_adjs)

        updated_verb1 = self.conjugate(verb1, 'present') 
        updated_verb2 = self.conjugate(verb2, 'present') 

        if pronouncing.rhymes(noun1):
            rhyme_b = random.choice(pronouncing.rhymes(noun1))
        else:
            rhyme_b = noun1

        limerick_lines = [
            f"There once was a {adj1} {theme},",
            f"Who {updated_verb1} by the {random.choice(rhymes)}.",
            f"But then with a {adj2} {noun1},",
            f"They {verb2} like a {adj3} {rhyme_b},",
            f"To rest by the {random.choice(rhymes)}."
        ]

        title = f"Something about {theme}"

        return Poem(title, limerick_lines)

    def evaluate_grammar(self, poem):
        tool = LanguageTool('en-US')
        errors = 0
        
        for line in poem.text:
            matches = tool.check(line)
            errors += len(matches)

        poem.set_grammar(errors)
        return errors

    def evaluate_sentiment(self, poem):
        total_sentiment = 0
        count = 0

        for line in poem.text:
            blob = TextBlob(line)
            for word in line.split():
                word_blob = TextBlob(word)
                if word_blob.sentiment.polarity != 0:
                    total_sentiment += word_blob.sentiment.polarity
                    count += 1
        
        score = total_sentiment / count if count > 0 else 0
        poem.set_sentiment(score)
        return score
                

def main():
    inspiring_set = InspiringSet()
    
    # need to append "collection/collection" to input
    author_folder = "collection/collection/Stuart Dybek"
    # generate poem from inspriring set
    inspiring_set.generate_inspiring_poems(author_folder)

    limericks = []
    highest_score = -999
    best_limerick = None

    for i in range(3):
        limerick = inspiring_set.generate_limerick()

        grammar_score = inspiring_set.evaluate_grammar(limerick)
        sentiment_score = inspiring_set.evaluate_sentiment(limerick)

        eval_score = sentiment_score / (grammar_score + 1)

        if eval_score > highest_score:
            highest_score = eval_score
            best_limerick = limerick

        limericks.append(limerick)

    print('"' + best_limerick.title + '"')
    print("\n".join(best_limerick.text))
    print(f"Grammar Errors: {inspiring_set.evaluate_grammar(best_limerick)}")
    print(f"Sentiment Score: {inspiring_set.evaluate_sentiment(best_limerick):.2f}")
    print(f"Score (Sentiment / Grammar): {highest_score:.2f}")


if __name__ == "__main__":
    main()