''' Starting point for ANLP 2016 assignment 2: CKY parsing'''
import re
import cfg_fix
from cfg_fix import parse_grammar, Tree
from cky_6 import CKY

def tokenise(tokenstring):
  '''Split a string into a list of tokens

  We treat punctuation as
  separate tokens, and split contractions into their parts.
  
  So for example "I'm leaving." --> ["I","'m","leaving","."]
  
  :type tokenstring: str
  :param tokenstring the string to be tokenised
  :rtype: list(str)
  :return: the tokens found in tokenstring'''
  return re.findall(
    # Fill in the regular expression needed on the next line
    # Use help(re.findall) and help(re) for information
    # You will need three sub-patterns:
    #   one for words and the first half of possessives
    #   one for the rest of possessives
    #   one for punctuation
      r'\b[a-zA-Z]+|\'?[a-zA-Z]+|[^ ]+',
    tokenstring)

grammar=parse_grammar("""
S -> NP VP
NP -> Det Nom | Nom | NP PP
Det -> NP "'s"
Nom -> N SRel | N
VP -> Vi | Vt NP | VP PP
PP -> Prep NP
SRel -> Relpro VP
Det -> 'a' | 'the'
N -> 'fish' | 'frogs' | 'soup' | 'children' | 'books'
Prep -> 'in' | 'for'
Vt -> 'saw' | 'ate' | 'read'
Vi -> 'fish' | 'swim'
Relpro -> 'that'
""")

print (grammar)
chart=CKY(grammar)
chart.recognise("the frogs swim".split()) # Should use
                                          # tokenise(s) once that's fixed
chart.pprint()

# Q1: Uncomment this once you've completed Q1
chart.recognise(tokenise("the frogs swim"),True)
# Q3 Uncomment the next three once when you're working on Q3
chart.recognise(tokenise("fish fish"))
chart.pprint()
chart.recognise(tokenise("fish fish"),True)

# Use this grammar for the rest of the assignment
grammar2=parse_grammar([
"S -> Sdecl '.' | Simp '.' | Sq '?' ",
"Sdecl -> NP VP",
"Simp -> VP",
"Sq -> Sqyn | Swhadv",
"Sqyn -> Mod Sdecl | Aux Sdecl",
"Swhadv -> WhAdv Sqyn",
"Sc -> Subconj Sdecl",
"NP -> PropN | Pro | NP0 ",
"NP0 -> NP1 | NP0 PP",
"NP1 -> Det N2sc | N2mp | Sc",
"N2sc -> Adj N2sc | Nsc | N3 Nsc",
"N2mp -> Adj N2mp | Nmp | N3 Nmp",
"N3 -> N | N3 N",
"N -> Nsc | Nmp",
"VP -> VPi | VPt | VPdt | Mod VP | VP Adv | VP PP",
"VPi -> Vi",
"VPt -> Vt NP",
"VPdt -> VPo PP",
"VPdt -> VPio NP",
"VPo -> Vdt NP",
"VPio -> Vdt NP",
"PP -> Prep NP",
"Det -> 'a' | 'the'",
"Nmp -> 'salad' | 'mushrooms'", 
"Nsc -> 'book' | 'fork' | 'flight' | 'salad' | 'drawing'",
"Prep -> 'to' | 'with'",
"Vi -> 'ate'",
"Vt -> 'ate' | 'book' | 'Book' | 'gave' | 'told'",
"Vdt -> 'gave' | 'told' ",
"Subconj -> 'that'",
"Mod -> 'Can' | 'will'",
"Aux -> 'did' ",
"WhAdv -> 'Why'",
"PropN -> 'John' | 'Mary' | 'NYC' | 'London'",
"Adj -> 'nice' | 'drawing'",
"Pro -> 'you' | 'he'",
"Adv -> 'today'"
])

chart2=CKY(grammar2)

# Note, please do _not_ use the Tree.draw() method uncommented
# _anywhere in this file_ (you are encouraged to use it in preparing
# your report).

# Q5 : run the recogniser on these sentences using chart2, and print the resulting matrix using chart2.pprint()
for s in ["John gave a book to Mary.",
          "John gave Mary a book.",
          "John gave Mary a nice drawing book.",
          "John ate salad with mushrooms with a fork.",
          "Book a flight to NYC.",
          "Can you book a flight to London?",
          "Why did John book the flight?",
          "John told Mary that he will book a flight today."]:
    print (s, chart2.recognise(tokenise(s)))
    chart2.pprint()


# Q8
# for s in [...]:
#     print s, chart2.parse(tokenise(s))
#     print chart2.first_tree().pprint()

# Q9
# for s in [...]:
#     print s, chart2.parse(tokenise(s))
#     for tree in chart2.all_trees():
#         print tree.pprint()




