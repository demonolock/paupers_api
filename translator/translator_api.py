from flask import Flask, request, jsonify

from translator import translate_word

app = Flask(__name__)

@app.route('/translate', methods=['GET'])
def translate_api():
    word = request.args.get('word')
    source_lang = request.args.get('source_lang', 'en')
    target_lang = request.args.get('target_lang', 'ru')

    if not word:
        return jsonify({"error": "No word provided"}), 400

    translation = translate_word(word, source_lang, target_lang)
    return jsonify({"word": word, "translation": translation})

if __name__ == '__main__':
    app.run(debug=True)
