class BottomUpParser:
    def __init__(self, grammar, start_symbol='s'):
        self.grammar = grammar
        self.start_symbol = start_symbol

    def parse(self, words):
        T = []          # Stack
        i = 0           # Input index
        steps = []      
        input_words = words.copy()

        while True:
            current_state = {
                "stack": list(T),
                "input_index": i,
                "action": None,
                "rule": None
            }

            # Try reduction first
            reduced = False
            for rule in self.grammar:
                lhs, rhs = rule
                required_length = len(rhs)
                
                if len(T) >= required_length:
                    # Get the top N elements from stack
                    top_part = T[-required_length:] if required_length > 0 else []
                    
                    # Direct comparison (no reversal needed)
                    if top_part == rhs:
                        # Perform reduction
                        del T[-required_length:]
                        T.append(lhs)
                        
                        current_state["action"] = "reduce"
                        current_state["rule"] = rule
                        steps.append(current_state)
                        reduced = True
                        break

            if reduced:
                continue  # Restart process after reduction

            # Try shifting with bracketed terminals
            if i < len(input_words):
                # Convert input word to bracketed form
                bracketed = f'[{input_words[i]}]'
                T.append(bracketed)
                current_state["action"] = "shift"
                steps.append(current_state)
                i += 1
                continue

            # Final acceptance check
            final_check = {
                "stack": list(T),
                "input_index": i,
                "action": "accept" if (len(T) == 1 and 
                                      T[0] == self.start_symbol and 
                                      i == len(input_words)) else "reject",
                "rule": None
            }
            
            if final_check["action"] == "accept":
                steps.append(final_check)
                return True, steps
            else:
                steps.append(final_check)
                return False, steps