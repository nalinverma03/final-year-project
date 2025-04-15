import json
from copy import deepcopy

def is_terminal(symbol):
    """Return True if the symbol is terminal (i.e. enclosed in square brackets)."""
    return symbol.startswith("[") and symbol.endswith("]")

class TopDownBtParser:
    def __init__(self, grammar):
        """
        Initialize the parser with the given grammar.
        
        grammar: a list of rules (tuples) where each rule is of the form:
                 (LHS, RHS) with RHS being a list of symbols.
        """
        self.grammar = grammar

    def parse(self, sentence):
        """
        Parse the input sentence.
        
        sentence: either a string or a list of tokens.
        Returns a tuple (success, steps) where success is True if parsing succeeded,
        and steps is the list of derivation steps.
        """
        # Check whether the sentence is already tokenized (a list) or a string.
        if isinstance(sentence, list):
            self.tokens = sentence
        else:
            self.tokens = sentence.split()
            
        # Initial stack is the start symbol, assumed to be "s".
        initial_stack = ["s"]
        result = self._parse_from(0, initial_stack, [])
        if result is not None:
            steps, i = result
            if i == len(self.tokens):
                accept_step = {
                    "action": "accept",
                    "input_index": i,
                    "rule": None,
                    "stack": []
                }
                steps.append(accept_step)
                return True, steps
        return False, []

    def _parse_from(self, i, stack, steps):
        """
        Recursive function that implements the top-down parser with backtracking.
        
        i: current index into the token list.
        stack: list of symbols (top of the stack is the last element).
        steps: list of actions recorded so far.
        
        Returns a tuple (steps, i) if successful, or None if the parse fails.
        """
        # NO MORE MOVES:
        if not stack:
            if i == len(self.tokens):
                return steps, i
            else:
                return None

        top = stack[-1]

        # LEAF CASE:
        if is_terminal(top):
            token_value = top[1:-1]  # remove the surrounding brackets
            if i < len(self.tokens) and self.tokens[i] == token_value:
                new_stack = stack[:-1]  # pop the terminal
                return self._parse_from(i + 1, new_stack, steps)
            else:
                return None

        # LEFT EXPANSION:
        # Get all grammar rules with LHS equal to the top-of-stack.
        alternatives = [rule for rule in self.grammar if rule[0] == top]
        for rule in alternatives:
            # Check if the rule is a leaf rule (i.e. RHS consists of a single terminal)
            if len(rule[1]) == 1 and is_terminal(rule[1][0]):
                terminal = rule[1][0][1:-1]
                if i < len(self.tokens) and self.tokens[i] == terminal:
                    step = {
                        "action": "leaf",
                        "input_index": i,
                        "rule": [rule[0], rule[1]],
                        "stack": deepcopy(stack)
                    }
                    new_stack = stack[:-1]  # pop the nonterminal
                    result = self._parse_from(i + 1, new_stack, steps + [step])
                    if result is not None:
                        return result
            else:
                # Expansion rule.
                step = {
                    "action": "expand",
                    "input_index": i,
                    "rule": [rule[0], rule[1]],
                    "stack": deepcopy(stack)
                }
                new_stack = stack[:-1]  # pop the nonterminal
                # Push RHS symbols in reverse order, so the leftmost symbol is on top.
                for symbol in reversed(rule[1]):
                    new_stack.append(symbol)
                result = self._parse_from(i, new_stack, steps + [step])
                if result is not None:
                    return result
        # No alternative worked; backtrack.
        return None