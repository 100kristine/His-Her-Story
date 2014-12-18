from collections import defaultdict
from nltk.corpus import stopwords
from nltk.util import bigrams,trigrams
import pickle,nltk
stop = set(stopwords.words())

data = pickle.load(open('tagged_tokenized_data_full_fromTheBride','r'))

def removeStopwords(text):
    #Remove stopwords
    return [word.lower() for word in text if len(word) > 2 and word.lower() not in stop]

class Graph:
    """Weighted undirected graph to model relationships between words. 
    Example:
    >>> graph = Graph()
    >>> graph.addObjs(objs)
    >>> graph.getFreq('family',10) #get the top n words related to family
    ['traditions',
     'performed',
     'mother',
     'friend',
     'ceremony',
     'wrote',
     'world',
     'wonderful',
     'well',
     'walk']
    """
    
    
    
    def __init__(self):
        def helpDict():
            #Can't pickle lambdas, use helper
            return defaultdict(int)
        self.graph = defaultdict(helpDict)

    def addObjs(self,data):
        #Adds word to graph
        count = 0
        for obj in data:
            if count%50 == 0:
                print count, " objects added"
            #categories = reduce(lambda x,y: x+y, [obj['categories'][key] for key in obj['categories'].keys()])
            #collapsed = categories + list(set(getTextItems(obj)))
            #for item in collapsed:
            #    for other in collapsed:
            #        if other != item:
            #            self.graph[item][other] += 1
            
            #pars = getTextItemsPar(obj)
            #for par in pars:
            #    self.addParagraph(par)
            
            for sentence in obj['tokens']:
                self.addParagraph(removeStopwords(sentence))
            count += 1
    
    def addParagraph(self,paragraph):
        for word in paragraph:
            for other in paragraph:
                if word != other:
                    self.graph[word][other] += 1
                    
    
    def getFreq(self,word,n):
        #Get top n frequencies of connected words
        top = [(self.graph[word][key],key) for key in self.graph[word].keys()]
        top.sort(reverse=True)
        return [top[i] for i in range(n)]
    
    def connections(self,word):
        return len(self.graph[word].keys())

	sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')

	def getTextItemsCollapsed(sample):
	    #Remove stopwords for all tokens and collapse into paragraph
	    return reduce(lambda x,y:x+y,[removeStopwords(item) for item in sample['tokens']])

	def getTextItemsPar(sample):
	    #Tokenize paragraph to add to graph
	    pars = []
	    for par in sample['paragraphs']:
	        pars.append(reduce(lambda x,y: x+y, [removeStopwords(nltk.word_tokenize(sent)) for sent in nltk.sent_tokenize(par)]))
	    return pars#reduce(lambda x,y:x+y,[removeStopwords(item) for item in sample['paragraphs']])

	def addTokens(sample):
	    return sample['tokens']

    