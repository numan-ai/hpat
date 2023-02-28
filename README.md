# hpat
## Hierarchical Pattern Matching 
Library to match hierarchical patterns in sequences with regexp-like patterns.  
Currently library is for text pattern matching but with some tweaks it is possible to match any sequences.

## Requirements and installation
This library requires Python3.9+.  
There are no other requirements or dependencies.  
Install by clonning this repo and running  
`python -m pip install .` inside the directory with the project.  

## Pattern
Strings are seqnences of concept `Character`, based on their values it is possible to match new concepts, here is an example:
```python
Pattern("Plus", [
    PatternNode(
        "Character", 
        value='+'
    )
]
```
This pattern matches a `Character` concept with a value `+`, `value` can be a list of all possible values:
```python
Pattern("ArithmeticSign", [
    PatternNode(
        "Character", 
        value=['+', '-', '/', '*']
    )
]
```
Concept can also be a list.

There are a lot of different parameters to tune how patterns match:

- `concept`: a single concept or a list of concepts to match
- `value`: a single value or a list of values to match
- `optional`: whether this pattern is optional
- `many`: match again if found, backtracking is automatic
- `id`: id of the node, allows to extract the matched value later
- `negate`: negates the result of the whole match (matched = didn't match, didn't match = match)
- `negate_value`: negates the result of value match
- `advance`: if False, the sequence cursor won't advance on match, and the next pattern will also be matching the same element.
- `at_start`: Analog of `^` in regexp
- `at_end`: Analog of `$` in regexp

## Simple Example
```python
import string

from hpat import (
    DataSequence,
    Extractor,
    Pattern,
    PatternNode,
    DictHierarchyProvider,
)


seq = DataSequence.from_string(" 732 + 94 ")

extractor = Extractor([
    Pattern("Digit", [
        PatternNode("Character", value=list(string.digits))]),
    Pattern("Number",
            pre=[PatternNode("Space"), ],
            nodes=[PatternNode("Digit", many=True), ],
            post=[PatternNode("Space"), ]),
    Pattern("Space", [
        PatternNode("Character", value=" ")]),
    Pattern("Plus", [
        PatternNode("Character", value="+")]),
    Pattern("Minus", [
        PatternNode("Character", value="-")]),
    Pattern("SimpleMathExpression", [
        PatternNode("Number"),
        PatternNode("Space", optional=True),
        PatternNode("Sign"),
        PatternNode("Space", optional=True),
        PatternNode("Number"),
    ]),
], DictHierarchyProvider({
    'Plus': ['Sign',],
    'Minus': ['Sign',],
}))

extractor.apply(seq)
seq.display()
```

Output:
```python
<WordSeparator " " [1]>, <Character " " [1]>, <Space " " [1]>
<SimpleMathExpression "732 + 94" [8]>, <Number "732" [3]>, <WordSeparator "7" [1]>, <Character "7" [1]>, <Digit "7" [1]>
<SimpleMathExpression "732 + 94" [8]>, <Number "732" [3]>, <WordSeparator "3" [1]>, <Character "3" [1]>, <Digit "3" [1]>
<SimpleMathExpression "732 + 94" [8]>, <Number "732" [3]>, <WordSeparator "2" [1]>, <Character "2" [1]>, <Digit "2" [1]>
<SimpleMathExpression "732 + 94" [8]>, <WordSeparator " " [1]>, <Character " " [1]>, <Space " " [1]>
<SimpleMathExpression "732 + 94" [8]>, <WordSeparator "+" [1]>, <Character "+" [1]>, <Plus "+" [1]>
<SimpleMathExpression "732 + 94" [8]>, <WordSeparator " " [1]>, <Character " " [1]>, <Space " " [1]>
<SimpleMathExpression "732 + 94" [8]>, <Number "94" [2]>, <WordSeparator "9" [1]>, <Character "9" [1]>, <Digit "9" [1]>
<SimpleMathExpression "732 + 94" [8]>, <Number "94" [2]>, <WordSeparator "4" [1]>, <Character "4" [1]>, <Digit "4" [1]>
<WordSeparator " " [1]>, <Character " " [1]>, <Space " " [1]>
```

Every line corresponds to a character in the string, lines list concepts that matched.  

## Filtering
Concepts can conflict and contradict each other but we keep all of them.  
Later it is up to the user how to remove wrong concepts, but we suggest to look for how many other concepts depend on a concept we a deciding to keep or remove.  
Use `seq.get_match_importance(match_id)` to get how many concepts depend on a given concept.  
We think that the more higher level concepts are dependand, the better given concept fitts the context.  
The idea is to keep all options and decide later what we think are the correct ones when more information is available.  
Example:  
word `run` can be a verb or a noun, so it would look like this:  
```python
<Word "run" [3]>, <Verb "run" [3]>, <Noun "run" [3]>, <Character "r" [1]>, <Letter "r" [1]>
<Word "run" [3]>, <Verb "run" [3]>, <Noun "run" [3]>, <Character "u" [1]>, <Letter "u" [1]>
<Word "run" [3]>, <Verb "run" [3]>, <Noun "run" [3]>, <Character "n" [1]>, <Letter "n" [1]>
```
Leter when we will have more context (`run as fast as you can`) we will be able to understand which part of speech it was, but we will still keep all the options in case new information will change our decision.  

## Hierarchies
In the example above we had "Sign" concept with two child concepts "Plus" and "Minus", it is possible to write your own hierarchy provider that will take information from outter source, for example from knowledge base:  
```python
class KBHierarchyProvider(HierarchyProvider):
    def get_parents(self, concept: str) -> list[str]:
        return knowledge_base.find_parents(concept)
```
