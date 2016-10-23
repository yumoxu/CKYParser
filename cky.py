import sys,re
import nltk
from collections import defaultdict
import cfg_fix
from cfg_fix import parse_grammar, CFG
from pprint import pprint
# The printing and tracing functionality is in a separate file in order
#  to make this file easier to read
from cky_print import CKY_pprint, CKY_log, Cell__str__, Cell_str, Cell_log

class CKY:
    """An implementation of the Cocke-Kasami-Younger (bottom-up) CFG recogniser.

    Goes beyond strict CKY's insistance on Chomsky Normal Form.
    It allows arbitrary unary productions, not just NT->T
    ones, that is X -> Y with either Y -> A B or Y -> Z .
    It also allows mixed binary productions, that is NT -> NT T or -> T NT"""

    def __init__(self,grammar):
        '''Create an extended CKY processor for a particular grammar

        Grammar is an NLTK CFG
        consisting of unary and binary rules (no empty rules,
        no more than two symbols on the right-hand side

        (We use "symbol" throughout this code to refer to _either_ a string or
        an nltk.grammar.Nonterminal, that is, the two thinegs we find in
        nltk.grammar.Production)

        :type grammar: nltk.grammar.CFG, as fixed by cfg_fix
        :param grammar: A context-free grammar'''

        self.verbose=False
        assert(isinstance(grammar,CFG))
        self.grammar=grammar
        # split and index the grammar
        self.buildIndices(grammar.productions())

    def buildIndices(self,productions):
        '''Q2: add docstring here, and add comments throughout'''
        self.unary=defaultdict(list)
        self.binary=defaultdict(list)
        for production in productions:
            rhs=production.rhs()
            lhs=production.lhs()
            assert(len(rhs)>0 and len(rhs)<=2)
            if len(rhs)==1:
                self.unary[rhs[0]].append(lhs)
            else:
                self.binary[rhs].append(lhs)

    def recognise(self,tokens,verbose=False):
        '''Q4: replace/expand this docstring, and add comments throughout
        Initialise a matrix from the sentence,
        then run the CKY algorithm over it
        Optional verbose argument controls debugging output, defaults to False '''
        self.verbose=verbose
        self.words = tokens
        self.n = len(self.words)+1
        self.matrix = []
        # We index by row, then column
        #  So Y below is 1,2 and Z is 0,3
        #    1   2   3  ...
        # 0  X   X   Z
        # 1      Y   X
        # 2          X
        # ...
        for r in range(self.n-1):
             # rows
             row=[]
             for c in range(self.n):
                 # columns
                 if c>r:
                     # This is one we care about, add a cell
                     row.append(Cell(r,c,self))
                 else:
                     # just a filler
                     row.append(None)
             self.matrix.append(row)
        self.unaryFill()
        self.binaryScan()
        # Replace the line below for Q6
        return self.grammar.start() in self.matrix[0][self.n-1].labels()

    def unaryFill(self):
        '''Q3: add docstring here, and add comments throughout'''
        for r in range(self.n-1):
            cell=self.matrix[r][r+1]
            word=self.words[r]
            cell.addLabel(word)
            cell.unaryUpdate(word)

    def binaryScan(self):
        '''The heart of the implementation:
            proceed across the upper-right diagonals
            in increasing order of constituent length'''
        for span in xrange(2, self.n):
            for start in xrange(self.n-span):
                end = start + span
                for mid in xrange(start+1, end):
                    self.maybeBuild(start, mid, end)

    def maybeBuild(self, start, mid, end):
        '''Q4: add docstring here, and add comments throughout'''
        self.log("%s--%s--%s:",start, mid, end)
        cell=self.matrix[start][end]
        for s1 in self.matrix[start][mid].labels():
            for s2 in self.matrix[mid][end].labels():
                if (s1,s2) in self.binary:
                    for s in self.binary[(s1,s2)]:
                        self.log("%s -> %s %s", s, s1, s2, indent=1)
                        cell.addLabel(s)
                        cell.unaryUpdate(s,1)

# helper methods from cky_print
CKY.pprint=CKY_pprint
CKY.log=CKY_log

class Cell:
    '''A cell in a CKY matrix'''
    def __init__(self,row,column,matrix):
        self._row=row
        self._column=column
        self.matrix=matrix
        self._labels=[]

    def addLabel(self,label):
        self._labels.append(label)

    def labels(self):
        return self._labels

    def unaryUpdate(self,symbol,depth=0,recursive=False):
        '''Q3: add docstring here, and add comments throughout'''
        if not recursive:
            self.log(str(symbol),indent=depth)
        if symbol in self.matrix.unary:
            for parent in self.matrix.unary[symbol]:
                self.matrix.log("%s -> %s",parent,symbol,indent=depth+1)
                self.addLabel(parent)
                self.unaryUpdate(parent,depth+1,True)

# helper methods from cky_print
Cell.__str__=Cell__str__
Cell.str=Cell_str
Cell.log=Cell_log

class Label:
    '''A label for a substring in a CKY chart Cell

    Includes a terminal or non-terminal symbol, possibly other
    information.  Add more to this docstring when you start using this
    class'''
    def __init__(self,symbol,
                 # Fill in here, if more needed
                 ):
        '''Create a label from a symbol and ...
        :type symbol: a string (for terminals) or an nltk.grammar.Nonterminal
        :param symbol: a terminal or non-terminal
        '''
        self._symbol=symbol
        # augment as appropriate, with comments

    def __str__(self):
        return str(self._symbol)

    def __eq__(self,other):
        '''How to test for equality -- other must be a label,
        and symbols have to be equal'''
        assert isinstance(other,Label)
        return self._symbol==other._symbol

    def symbol(self):
        return self._symbol
    # Add more methods as required, with docstring and comments
