import textstat
from glob import glob
import json
import spacy
import random
import pronouncing


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
            for line in poem.text:
                doc = self.nlp(line)
                line_nouns = ([token.text for token in doc if token.pos_ == "NOUN"])
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
                line_adjectives = ([token.text for token in doc if token.pos_ == "ADJ"])
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
                line_verbs = ([token.text for token in doc if token.pos_ == "VERB"])
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
                line_prepositions = ([token.text for token in doc if token.pos_ == "ADP"])
                if line_prepositions:
                    prepositions.append(line_prepositions)
        return prepositions


    def generate_limerick(self):
        '''
        Uses inspiring set to generate the limerick, which uses a AABBA Rhyme scheme.
        '''
        nouns = [word for sublist in self.generate_nouns() for word in sublist]
        adjectives = [word for sublist in self.generate_adjectives() for word in sublist]
        verbs = [word for sublist in self.generate_verbs() for word in sublist]
        prepositions = [word for sublist in self.generate_prepositions() for word in sublist]


        first_noun = random.choice(nouns)
        second_noun = random.choice(nouns)
        third_noun = random.choice(nouns)

        first_prep = random.choice(prepositions)
        second_prep = random.choice(prepositions)
        third_prep = random.choice(prepositions)
        fourth_prep = random.choice(prepositions)
        fifth_prep = random.choice(prepositions)

        first_verb = random.choice(verbs)
        second_verb = random.choice(verbs)
        third_verb = random.choice(verbs)
        fourth_verb = random.choice(verbs)

        first_adj = random.choice(adjectives)
        second_adj = random.choice(adjectives)
        third_adj = random.choice(adjectives)
        fourth_adj = random.choice(adjectives)

        # handles errors when attempting to find rhymes for 2 & 5
        if (len(pronouncing.rhymes(second_noun)) > 1):
            rhymeA = pronouncing.rhymes(second_noun)[0]
            rhymeAA = pronouncing.rhymes(second_noun)[1]
        elif len(pronouncing.rhymes(second_noun)) == 1:
            rhymeA = pronouncing.rhymes(second_noun)[0]
            rhymeAA = rhymeA
        else:
            rhymeA = second_noun

        # handles errors when attempting to find rhymes for 4
        if (len(pronouncing.rhymes(third_noun)) != 0):
            rhymeB = pronouncing.rhymes(third_noun)[0]
        else:
            rhymeB = second_noun
        
        # generic limerick. Will aim to create more accurate and coherent structure
        starting_line = f"There once was a {first_noun} {first_prep} {second_noun}"
        second_line = f"Who {first_adj} {first_verb} {second_prep} {rhymeA}.\n"
        third_line = f"The {second_noun} {second_adj} {second_verb} {third_prep} {third_noun}\n"
        fourth_line = f"And {third_adj} {third_verb} {fourth_prep} {rhymeB}.\n"
        firth_line = f"{first_noun} {fourth_verb} {fourth_adj} {fifth_prep} {rhymeAA}."

        poem_title = starting_line
        starting_line += '\n'
        poem_lines = [starting_line, second_line, third_line, fourth_line, firth_line]

        return Poem(poem_title, poem_lines)

def main():
    inspiring_set = InspiringSet()
    
    # need to append "collection/collection" to input
    author_folder = "collection/collection/Alice Moore Dunbar-Nelson"
   
    # generate poem from inspriring set
    inspiring_set.generate_inspiring_poems(author_folder)

    limerick = inspiring_set.generate_limerick()

    print('"' + limerick.title + '"')
    print("\n".join(limerick.text))

if __name__ == "__main__":
    main()
    
