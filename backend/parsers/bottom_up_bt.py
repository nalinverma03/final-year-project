import json
from copy import deepcopy

class BottomUpBtParser:
    def __init__(self, grammar):
        """
        Initialize the parser with the given grammar.
        
        grammar: a list of rules where each rule is a tuple (LHS, RHS)
                 with RHS being a list of symbols. Terminals are written 
                 in square brackets (e.g. "[the]").
        """
        self.grammar = grammar

    def parse(self, sentence):
        """
        Parse the input sentence using a bottom–up, shift–reduce parser 
        with backtracking.
        
        sentence: a string or list of tokens. (If a string is provided, it is tokenized.)
        
        Returns a tuple (success, steps) where success is a Boolean indicating 
        if the parse succeeded and steps is a list of move dictionaries.
        """
        # If the sentence is already a list (e.g. pre‐tokenized), use it; otherwise tokenize.
        if isinstance(sentence, list):
            self.tokens = sentence
        else:
            self.tokens = sentence.split()
        # Start with an empty working stack (T) and input pointer i = 0.
        steps = self._parse([], 0, [])
        if steps is not None:
            # Append final accept move. (We log the input index as the last token index.)
            last_index = len(self.tokens) - 1 if self.tokens else 0
            final_step = {
                "action": "reduce",
                "input_index": last_index,
                "rule": None,
                "stack": ["s"]
            }
            steps.append(final_step)
            return True, steps
        else:
            return False, []

    def _parse(self, T, i, steps):
        """
        Recursive function that performs the shift–reduce moves with backtracking.
        
        T: list (stack) containing symbols accumulated so far.
        i: current index into self.tokens (0–based).
        steps: list of steps (each a dict) recorded so far.
        
        Returns the steps list if a complete parse is achieved (i.e. T == ["s"] and
        all tokens have been consumed), otherwise returns None.
        """
        # For logging purposes, let log_i be the current input index 
        # (if i is beyond the end, use the index of the last token).
        log_i = i if i < len(self.tokens) else (len(self.tokens) - 1 if self.tokens else 0)
        
        # If the working stack T is exactly ["s"] (the start symbol)
        # and we have consumed all the tokens, then we have succeeded.
        if T == ["s"] and i == len(self.tokens):
            return steps
        
        # --- TRY REDUCING THE STACK ---
        # Loop through the grammar rules (from first to last) to try a reduction.
        for rule in self.grammar:
            lhs, rhs = rule
            N = len(rhs)
            # Check if the top N symbols of T match the rule's RHS.
            if len(T) >= N and T[-N:] == rhs:
                # Record the reduce move (log the current state before reducing)
                new_steps = steps + [{
                    "action": "reduce",
                    "input_index": log_i,
                    "rule": [lhs, rhs],
                    "stack": deepcopy(T)
                }]
                # Perform the reduction: remove the matched symbols and push the LHS.
                new_T = T[:-N] + [lhs]
                # Recursively try further moves with the updated state.
                result = self._parse(new_T, i, new_steps)
                if result is not None:
                    return result
        # --- TRY SHIFTING A WORD ---
        # If no reduction is applicable and there is an unprocessed input token,
        # record a shift move.
        if i < len(self.tokens):
            new_steps = steps + [{
                "action": "shift",
                "input_index": i,
                "rule": None,
                "stack": deepcopy(T)
            }]
            # Shift: push the next input token onto the stack.
            # (Wrap the token in square brackets so it matches the terminal format in the grammar.)
            token = self.tokens[i]
            new_T = T + ["[{}]".format(token)]
            # Increment the input pointer.
            result = self._parse(new_T, i + 1, new_steps)
            if result is not None:
                return result
        
        # --- NO MOVE AVAILABLE: BACKTRACK ---
        # If there is no applicable reduction and no token remains to shift, then this branch fails.
        return None