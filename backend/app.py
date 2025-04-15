from flask import Flask, request, jsonify
from flask_cors import CORS
from parsers import TopDownParser
from parsers.bottom_up import BottomUpParser  # Import BottomUpParser

app = Flask(__name__)
CORS(app)

def parse_grammar(grammar_text):
    grammar = []
    for line in grammar_text.strip().split('\n'):
        lhs, rhs = line.split('-->')
        lhs = lhs.strip().lower()
        rhs_parts = []
        
        for part in rhs.strip().split(','):
            part = part.strip().lower()
            rhs_parts.append(part)
                
        grammar.append((lhs, rhs_parts))
    return grammar

@app.route('/parse', methods=['POST'])
def parse():
    data = request.json
    sentence = data['sentence'].lower().split()  # Split into words
    grammar = parse_grammar(data['grammar'])
    algorithm = data['algorithm']

    if algorithm == "top-down":
        parser = TopDownParser(grammar)
        success, steps = parser.parse(sentence)
        return jsonify({"success": success, "steps": steps})
    elif algorithm == "bottom-up":
        parser = BottomUpParser(grammar)
        success, steps = parser.parse(sentence)
        return jsonify({"success": success, "steps": steps})
    else:
        return jsonify({"error": "Algorithm not supported"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
    # print(parse_grammar("s --> np,vp\nnp --> det,n\ndet --> [the]\nn --> [man]\nn --> [dog]\nvp --> tv,np\ntv --> [hit]"))
    # print(parse_grammar("s --> [a],s,[b]\ns --> [a],[b]"))