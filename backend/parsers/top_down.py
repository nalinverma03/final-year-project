class TopDownParser:
    def __init__(self, grammar, start_symbol='s'):
        self.grammar = grammar  # List of (LHS, RHS) tuples
        self.start_symbol = start_symbol

    def _unquote_terminal(self, symbol):
        """Strip quotes from terminal symbols if present"""
        if isinstance(symbol, str) and symbol.startswith('[') and symbol.endswith(']'):
            return symbol[1:-1]
        return symbol

    def parse(self, words):
        F = [self.start_symbol]  # Initial stack with start symbol
        i = 0       # Current input index
        steps = []   # Track states for visualization

        while True:
            current_state = {
                "stack": list(F),
                "input_index": i,
                "action": None,
                "rule": None
            }

            # Check for success/failure
            if not F and i == len(words):
                current_state["action"] = "accept"
                steps.append(current_state)
                return True, steps
            if not F or i > len(words):
                current_state["action"] = "reject"
                steps.append(current_state)
                return False, steps

            A = F[-1]  # Top of the stack
            applied = False

            # Check all rules in order for current non-terminal
            for lhs, rhs in self.grammar:
                if lhs != A:
                    continue  # Skip rules for other non-terminals

                # Handle epsilon production
                if rhs == ['ε']:
                    F.pop()
                    current_state["action"] = "expand"
                    current_state["rule"] = (lhs, rhs)
                    applied = True
                    break

                # Handle terminal production
                if len(rhs) == 1:
                    raw_terminal = rhs[0]
                    terminal = self._unquote_terminal(raw_terminal)
                    
                    if i < len(words) and terminal == words[i]:
                        F.pop()
                        i += 1
                        current_state["action"] = "leaf"
                        current_state["rule"] = (lhs, rhs)
                        applied = True
                        break
                    else:
                        continue  # Try next rule

                # Handle non-terminal expansion
                F.pop()
                for symbol in reversed(rhs):
                    F.append(symbol)
                current_state["action"] = "expand"
                current_state["rule"] = (lhs, rhs)
                applied = True
                break  # Stop after first applicable rule

            if applied:
                steps.append(current_state)
                continue

            # Handle terminal at top of stack
            stack_terminal = self._unquote_terminal(A)
            if i < len(words) and stack_terminal == words[i]:
                F.pop()
                i += 1
                current_state["action"] = "leaf"
                current_state["rule"] = (A, [A])
                steps.append(current_state)
            else:
                current_state["action"] = "reject"
                steps.append(current_state)
                return False, steps