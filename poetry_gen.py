import textstat
from glob import glob
import json
import spacy
import numpy


class Poem:
    def __init__(self, title, text):
        self.title = title
        self.text = text


class InspiringSet:
    def __init__(self):
        self.inspiring_poems = []
        self.nlp = spacy.load("en_core_web_sm")


    def generate_inspiring_poems(self, authors_poems):
        '''
        Function that helps find and extract the poems by the specified author
        '''
        author_folder = glob(f"{authors_poems}/*.json") # helps located folder in this repo

        for poem in author_folder:
            with open(poem, 'r', encoding='utf-8') as f:
                file_contents = json.load(f)
                title = file_contents.get('title')
                text = file_contents.get('text')
                extracted_poem = Poem(title, text)
                self.inspiring_poems.append(extracted_poem) # add poem to inspo set
    
    
    def generate_nouns(self):
        '''
        Identifies nouns within the poems of the author
        '''
        nouns = []
        for poem in self.inspiring_poems:
            for line in poem.text:
                doc = self.nlp(line)
                line_nouns = ([token.text for token in doc if token.pos_ == "NOUN"]) # finds nouns in lines
                if line_nouns:
                    nouns.append(line_nouns)
        return nouns

    def generate_adjectives(self):
        '''
        Identifies adjectives within the poems of the author
        '''
        adjectives = []
        for poem in self.inspiring_poems:
            for line in poem.text:
                doc = self.nlp(line)
                line_adjectives = ([token.text for token in doc if token.pos_ == "ADJ"]) # finds adjecticves in lines
                if line_adjectives:
                    adjectives.append(line_adjectives)
        return adjectives

    def generate_verbs(self):
        '''
        Identifies verbs within the poems of the author
        '''
        verbs = []
        for poem in self.inspiring_poems:
            for line in poem.text:
                doc = self.nlp(line)
                line_verbs = ([token.text for token in doc if token.pos_ == "VERB"])  # finds verbs in lines
                if line_verbs:
                    verbs.append(line_verbs)
        return verbs

    def generate_prepositions(self):
        '''
        Identifies prepositions within the poems of the author
        '''
        prepositions = []
        for poem in self.inspiring_poems:
            for line in poem.text:
                doc = self.nlp(line)
                line_prepositions = ([token.text for token in doc if token.pos_ == "ADP"])  # finds prepositions in lines
                if line_prepositions:
                    prepositions.append(line_verbs)
        return prepositions


    def generate_limerick(self):
        '''
        Uses inspiring set to generate the limerick, which uses a AABBA Rhyme scheme.
        '''
        nouns = self.generate_nouns()
        adjectives = self.generate_adjectives()
        verbs = self.generate_verbs()
        prepositions = self.generate_prepositions()

        first_noun = 
        second_noun = 
        third_noun = 

        first_prep =
        second_prep =
        third_prep = 
        fourth_prep =
        fifth_prep = 

        first_verb = 
        second_verb =
        third_verb = 
        fourth_verb = 

        first_adj = 
        second_adj = 
        third_adj = 
        fourth_adj = 

        rhymeA = pronouncing.rhymes(second_noun)[0]
        rhymeB = pronouncing.rhymes(third_noun)[0]
        rhymeAA = pronouncing.rhymes(second_noun)[0]

        starting_line = f"There once was a {first_noun} {first_prep} {second_noun}"
        second_line = f"Who {first_adj} {first_verb} {second_prep} {rhymeA}."
        third_line = f"The {second_noun} {second_adj} {second_verb} {third_prep} {third_noun}"
        fourth_line = f"And {third_adj} {third_verb} {fourth_prep} {rhymeB}."
        firth_line = f"{first_noun} {fourth_verb} {fourth_adj} {fifth_prep} {rhymeAA}"

        poem_lines = [starting_line, second_line, third_line, fourth_line, firth_line]
        poem_title = starting_line

        return Poem(poem_title, poem_lines)

def main():
    inspiring_set = InspiringSet()
    author_folder = "collection/collection/A. E. Housman" # need to appened collection/collection from input

if __name__ == "__main__":
    main()
    
