#STD LIBRARIES
from optparse import OptionParser
import math, random, copy

#CUSTOM LIBRARIES
import en #NLP library
from wordnik import * #dictionary with part of speech, synonyms, related word
apiUrl = 'http://api.wordnik.com/v4'
apiKey = '1453b0da46be3985ab0040b354601405dbb094b3e77e51454'
client = swagger.ApiClient(apiKey, apiUrl)

#FILES
import searchutil, util
from poetry import * 
from grammar import *

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-n', '--n-gram', type='int', dest='ngrams', default=1)
    parser.add_option('-f', '--file', dest='filename', default=1)
    parser.add_option('-o', '--output', type='int', dest='npoems', default=3)
    (options, args) = parser.parse_args()
 
# Generate poetry based on a corpus       
def generate(corpus):
    parameters = [(8,[]) for _ in range(8)] #stub, assumed 8 syllables (words) per line
    poem = Poetry(parameters)
    grammar = Grammar(corpus.frequency_map, corpus.word_map)

    while not poem:
        curr = poem.getLine()
        while curr:
            word = grammar.next()
            if not word: # Seed has no successsor words
                break
            if not curr.add(word):
                # Word doesn't fit, try a different one
                # Will get stuck here under a rigid syllable counting system
                # Need to add flexibility within grammar to prevent failure
                # See util.getSyllables
                continue
            grammar.update(word) #word added successfully, update seed
        poem.iterate()
    return poem.format()

class PoetrySearchProblem(searchutil.SearchProblem):
    def __init__(self, poem, grammar): self.poem, self.grammar = poem, grammar
    def startState(self): return self.poem, None
    def isGoal(self, state):
        poem, seed = state
        return poem
    # Return a list of (action, newState, cost) tuples corresponding to edges
    # coming out of |state|.
    def succAndCost(self, state):
        poem, seed = state
        if not seed: #initialize seed
            seed = util.weightedRandomChoice(self.grammar.frequency_map)
            new_poem = poem
            words = ""
            for i in range(len(seed)):
                new_poem.getLine().add(seed[i])
                self.poem = new_poem
            return [(seed, (new_poem, seed), 0)]
        result = []
        for word in self.grammar.word_map[seed]:
            cost = 0
            new_poem = copy.deepcopy(poem)
            print new_poem.format()
            curr = new_poem.getLine()
            if curr: 
                if curr.add(word):
                    if poem.currentLine != new_poem.currentLine: #favor forward progress
                        cost = -100
                    broken_seed = [seed[i] for i in range(len(seed))]
                    broken_seed.pop(0)
                    broken_seed.append(word)
                    new_seed = tuple(broken_seed)
                    if not curr: #previous line was completed
                        new_poem.iterate()
                    self.poem = new_poem #sneaky
                    result.append((word, (new_poem, new_seed), cost))
        return result

#########################################################################
# MAIN EXECUTION
#########################################################################

corpus = Corpus(options.filename)
corpus.analyze(options.ngrams)

#NEW 
parameters = [(8,[]) for _ in range(2)] #stub, assumed 8 syllables (words) per line
poem = Poetry(parameters)
grammar = Grammar(corpus.frequency_map, corpus.word_map)
problem = PoetrySearchProblem(poem, grammar)
ucs = searchutil.UniformCostSearch(verbose=5)
ucs.solve(problem)
print problem.poem.format()
#NEW


# for i in range(options.npoems):
#     output = generate(corpus)
#     print output
# END