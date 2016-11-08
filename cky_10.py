import sys,re
import nltk
from collections import defaultdict
import cfg_fix
from cfg_fix import parse_grammar, CFG
from pprint import pprint
# The printing and tracing functionality is in a separate file in order
#  to make this file easier to read
from cky_print import CKY_pprint, CKY_log, Cell__str__, Cell_str, Cell_log
import test

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
        '''Q2: add docstring here, and add comments throughout
        Function: Splitting rules into unary ruls and binary rules, then storing these rules in different
        defaultdicts( one type of class, like dictionary)
        For example: 1.S -> NP VP  2.VP -> V
        We store 1 in a defaultdicts called binary and store 2 in a defaultdicts called unary

        How this function works:
        Tips: we use defaultdict to store rules
        At first, it creates two defaultdicts( one type of class, like dictionary), one for productions which
        have only one nonterminal or terminal in the right side(unary rules) and another for productions having
        two nonterminals or terminals.(binary rules)
        Secondly, it uses a loop to get each production and gets objects in the left-hand side and in the right-hand
        side of this Production respectively.
        Finally, after correcting the number of objects in the right-hand side, if the number of nonterminals
        and terminals in the right-hand side of this production is 1, this function stores the nonterminal in the
        left-hand side as the value and the nonterminal or terminal in the right-hand side as the key in the
        unary defaultdict. If the number is 2, this function stores the nonterminal in the left-hand side as
        the value and the nonterminals or terminals in the right-hand side as the key in the binary.

        :type productions: nltk.grammar.Production, as fixed by cfg_fix
        :param productions: the productions to be split and stored in a new way
        '''

        self.unary=defaultdict(list)
        self.binary=defaultdict(list)
        for production in productions:
            rhs=production.rhs()
            lhs=production.lhs()
            # Ensuring no more than two symbols on the right-hand side
            assert(len(rhs)>0 and len(rhs)<=2)
            if len(rhs)==1:
                # add unary rules
                self.unary[rhs[0]].append(lhs)
            else:
                # add binary rules
                self.binary[rhs].append(lhs)

    def parse(self,tokens,verbose=False):
        '''Q4: replace/expand this docstring, and add comments throughout
        Initialise a matrix from the sentence,
        then run the CKY algorithm over it
        Optional verbose argument controls debugging output, defaults to False

        At first, we initialise a matrix which contains cells in the right of the diagonal.
        Secondly, we fill all matrix's diagonal cells for each words through function unaryFill.
        Then we use CKY algorithm to fill some cells which attach the condition in the right of the diagonal.
        Finally, we find the start nonterminal and return it.

        :type tokens: str
        :param tokens: a string to be used to build a matrix through CKY algorithm
        :type verbose: bool
        :param verbose: a bool to controls debugging output

        :rtype self.grammar.start(): str
        :param self.grammar.start(): the start symbol of the grammar
        '''

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
        # Filling all the relative unary rules
        self.unaryFill()
        # Adding all the binary rules
        self.binaryScan()
        # Replace the line below for Q6
        # collect final symbols from final labels
        final_symbols = [label.symbol() for label in self.matrix[0][self.n-1].labels()]
        if self.grammar.start() in final_symbols:
            # Calculating the number of successful analyses
            Analyses_n = 0
            for symbol in final_symbols:
                if symbol == self.grammar.start():
                    Analyses_n += 1
            return Analyses_n
        else:
            return False

    def unaryFill(self):
        '''Q3: add docstring here, and add comments throughout
        Function: Filling matrix's diagonal cells for each words

        How this function works:
        For each word, the location of the initial cell is on the diagonal, so we firstly get the word and the cell
        which is link to this word.
        Then we add this word into this cell.
        Finally, we update the content of this cell( Completing all the relative unary rules ).
        '''

        for r in range(self.n-1):
            cell=self.matrix[r][r+1]
            word=self.words[r]
            cell.addLabel(Label(word))  # leaf node with no child

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
        '''Q4: add docstring here, and add comments throughout
        Function: Filling matrix through CKY algorithm and binary rules
        How this function works:
        When we get integer start, mid and end, it means we get two cells, cell(start, mid) and cell(mid, end)
        At first, we judge whether there are binary rules in the right-hand side of which contains symbols of these
        two cells
        Then if we find binary rules satisfying the condition, we add the left-hand side nonterminal into
        the cell(start, end).
        Finally, updating this cell.

        :type start, mid, end:int
        :param start: the start index of the first cell
        :param mid: the end index of the first cell and the start index of the second cell
        :param end: the end index of the second cell
        '''

        self.log("%s--%s--%s:",start, mid, end)
        cell=self.matrix[start][end]
        for s1 in self.matrix[start][mid].labels():  # left child label
            for s2 in self.matrix[mid][end].labels():  # right child label
                # find the binary rules like s -> s1 s2
                s1_symbol = s1.symbol()
                s2_symbol = s2.symbol()
                if (s1_symbol,s2_symbol) in self.binary:
                # if (s1,s2) in self.binary:
                    for s_symbol in self.binary[(s1_symbol,s2_symbol)]:
                        self.log("%s -> %s %s", s_symbol, s1_symbol, s2_symbol, indent=1)
                        # add the symbol and update this cell
                        label = Label(s_symbol,s1,s2)
                        cell.addLabel(label,1)

    def firstTree(self):
        '''
            Construct the first parse tree based upon utilizing pre-order traversal to generate the string for parsing.
            Non-recursive approach is adopted for the sake of computational efficiency.

        :return: the first parse tree if the parsing is successful and else None.
        '''
        symbols = []
        final_label = self.matrix[0][self.n-1].labels()[0]
        if self.grammar.start() == final_label.symbol():
            stack = []
            node = final_label
            while node or stack:
                while node:
                    if node.lchild() or node.symbol() in {'.', '?'}:
                        symbols.append('(')
                        symbols.append(str(node.symbol()))
                        if node.lchild():
                            stack.append(node)
                        else:
                            symbols.append(')')
                    # leaf node
                    else:
                        symbols.append(' ')
                        symbols.append(str(node.symbol()))
                    node = node.lchild()

                # the leftest child has been processed, now comes to the right child of the latest node
                if not stack:
                    break
                node = stack[-1]

                # loop to find nodes with two children
                # for nodes with only one child, just add ')' to symbols and skip it
                while not node.rchild():  # one child
                    symbols.append(')')
                    stack.pop()
                    if not stack:
                        break
                    node = stack[-1]

                # loop to find nodes that has not been checked
                # for checked nodes, just add ')' to symbols and skip it
                while node.is_rchild_checked():
                    symbols.append(')')  # end the subtree
                    stack.pop()
                    if not stack:
                        break  # if break from here, the node is also a checked one
                    node = stack[-1]

                # break from the last loop, indicating the node is the last node 'S'
                if node.is_rchild_checked():
                    break
                # check its right child
                else:
                    node.set_rchild_checked(True)
                    node = node.rchild()

            tree_str = ' '.join(symbols)
            return nltk.Tree.fromstring(tree_str)
        else:
            return  None

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

    def addLabel(self,label,depth=0,recursive=False):
        '''
            Add given label to the cell.

        :param label: instance of Label class.
        :param depth: the depth of recurse.
        :param recursive: whether the label is recursive.
        :return:
        '''
        # do nothing if the same label has already existed.
        if label.symbol() not in [l.symbol() for l in self.labels()]:
            self._labels.append(label)
            # Call unaryUpdate to update check unary rules and add new label
            self.unaryUpdate(label,depth,recursive)

    def labels(self):
        return self._labels

    def unaryUpdate(self,label,depth=0,recursive=False):
        '''Q3: add docstring here, and add comments throughout
        Function: Updating a CKY matrix through unary rules
        How this function works:
        If we do not want to recurse, we just print the symbol and the location of this cell.
        If there are rules containing this symbol, we should add the nonterminal of this rule in this cell as a
        label(symbol) and then we have to use recursive algorithm to add all relative unary branching rules in
        this cell.

        :type symbol: str
        :param symbol: a symbol to be used to find relative unary rules in this cell
        :type depth: int
        :param depth: the depth of this symbol in this cell
        :type recursive: boolean
        :param recursive: a boolean telling us whether we should recurse this function
        '''

        symbol = label.symbol()
        if not recursive:
            self.log(str(symbol),indent=depth)
        if symbol in self.matrix.unary:
            for parent in self.matrix.unary[symbol]:
                # depth + 1, because of adding an unary rule
                self.matrix.log("%s -> %s",parent,symbol,indent=depth+1)
                # if unary, regard the only child as the left child
                parent_label = Label(parent, lchild=label)
                self.addLabel(parent_label,depth+1,True)

# helper methods from cky_print
Cell.__str__=Cell__str__
Cell.str=Cell_str
Cell.log=Cell_log


class Label:
    '''A label for a substring in a CKY chart Cell

    Includes a terminal or non-terminal symbol, possibly other
    information.  Add more to this docstring when you start using this
    class'''
    def __init__(self,symbol,lchild=None,rchild=None,is_rchild_checked=False):
        '''Create a label from a symbol and ...
        :type symbol: a string (for terminals) or an nltk.grammar.Nonterminal
        :param symbol: a terminal or non-terminal
        :param lchild: the left child
        :param rchild: the right child
        '''
        self._symbol=symbol
        self._lchild=lchild
        self._rchild=rchild
        self._is_rchild_checked=is_rchild_checked

        # augment as appropriate, with comments

    def __str__(self):
        return str(self._symbol)

    def __eq__(self,other):
        '''How to test for equality -- other must be a label,
        and symbols have to be equal'''
        assert isinstance(other,Label)
        return (self._symbol==other._symbol and self._lchild._symbol == other._lchild._symbol and self._rchild._symbol==other._rchild._symbol)

    def symbol(self):
        return self._symbol
    # Add more methods as required, with docstring and comments

    def lchild(self):
        return self._lchild

    def rchild(self):
        return self._rchild

    def is_rchild_checked(self):
        return self._is_rchild_checked

    def set_rchild_checked(self, is_rchild_checked):
        self._is_rchild_checked = is_rchild_checked