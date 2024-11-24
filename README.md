Title: InSpoet
Author: Emre Andican

Description: Limerick Generator that aims to create limericks based on
themes from a collection of over 1000 poets (specify which poet). Uses
TF-IDF scores and a template to generate limericks based on a specificed
poet from the user. Evaluates generated limericks through sentiment score
and total grammatical errors.

Set-Up:

1. Run poetry_gen.py
2. go to server (http://127.0.0.1:5001/)
3. Enter in a poet/leave blank (need to be ultra-meticulous about spelling.
   Please see collection to find an poet and copy name)
4. Click "Start Generating!"
5. Watch and listen to limerick being generated.
6. Optional: View all saved limericks that you have generated

Challenges:

1. I really need to brush up on the concepts of TF-IDF. Thankfully this course,
   my data-science course, and other experiences have given me the idea to implement this
   but I had to make sure my algorithm was working fully (took me a while) so that I
   could find siginificant terms within each poem of the author I was analyzing
2. I tried using n-grams for generation originally, but the JSON files containing the poems
   were pretty complicated to work with. Me, being the impatient student I am, decided that I
   should find another route. I found a paper that mentioned templates as a way to generate
   poems, so I blended the creativity I derived from using pronouncing's rhymes, GloVe's embedded
   words, and the themes I sourced from my TF-IDF function in order to place them in a readable
   template. Took me a while to piece this together
3. Using/implementing GloVe took me a while. Mostly because the GloVe files are so massive and
   there are supporting packages that I needed to use to make my work a little bit more efficient
4. The HTML piece was a little painful. I have a lot fo experience with HTML, but actually implementing
   Flask was a long experience for me. I tried many different methods before actually being able to
   create a website that was sufficient enough to present to you.

Papers:

1. Gervás, Pablo. "Propp’s Morphology of the Folk Tale as a Grammar for Generation." AISB 2013 Convention Proceedings: Computational Creativity in Narrative Systems, 2013. http://nil.fdi.ucm.es/sites/default/files/GervasAISB2013CRC.pdf.
2. Linardaki, Christina. "Poetry at the First Steps of Artificial Intelligence." Humanist Studies & the Digital Age 2, no. 1 (2012). https://journals.oregondigital.org/hsda/article/view/5759/7542.
   (For TF-IDF inspiration)
3. Zhang, Xingxing, and Mirella Lapata. "Sentence Simplification with Deep Reinforcement Learning." Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing, 2018, 595–606. https://aclanthology.org/D18-1353.pdf.
