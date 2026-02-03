from flask import Flask, request, jsonify, render_template_string
import azure.cognitiveservices.speech as speechsdk

# ---------------- CONFIG ---------------- #
SPEECH_KEY = "YOUR_AZURE_SPEECH_KEY"
REGION = "YOUR AZURE_REGION"

LANGUAGES = {
    "en-US": "English",
    "hi-IN": "Hindi",
    "fr-FR": "French",
    "es-ES": "Spanish",
    "de-DE": "German",
}

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Azure Speech Web App</title>
<style>
body{font-family:Arial;background:#f4f4f4;padding:30px}
.container{background:white;padding:20px;border-radius:10px;max-width:600px;margin:auto}
button{padding:10px;margin:5px}
select,input{padding:8px;margin:5px;width:100%}
</style>
</head>
<body>
<div class="container">
<h2>Azure Speech Services Web App</h2>

<h3>Text to Speech</h3>
<input id="ttsText" placeholder="Enter text">
<select id="ttsLang">
{% for k,v in langs.items() %}
<option value="{{k}}">{{v}}</option>
{% endfor %}
</select>
<button onclick="tts()">Speak</button>

<h3>Speech to Text + Translation</h3>
<select id="transLang">
{% for k,v in langs.items() %}
<option value="{{k}}">{{v}}</option>
{% endfor %}
</select>
<button onclick="stt()">Record & Translate</button>
<p id="result"></p>

<script>
function tts(){
 fetch('/tts',{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({text:ttsText.value,lang:ttsLang.value})});
}

function stt(){
 fetch('/stt',{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({lang:transLang.value})})
 .then(res=>res.json()).then(d=>result.innerText=d.text)
}
</script>
</div>
</body>
</html>
"""

# ---------------- ROUTES ---------------- #
@app.route('/')
def home():
    return render_template_string(HTML, langs=LANGUAGES)

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data['text']
    lang = data['lang']

    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=REGION)
    speech_config.speech_synthesis_language = lang

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    synthesizer.speak_text_async(text)

    return "ok"

@app.route('/stt', methods=['POST'])
def stt():
    data = request.json
    lang = data['lang']

    trans_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=SPEECH_KEY,
        region=REGION
    )

    trans_config.speech_recognition_language = "en-US"
    trans_config.add_target_language(lang.split('-')[0])

    audio = speechsdk.AudioConfig(use_default_microphone=True)

    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=trans_config,
        audio_config=audio
    )

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.TranslatedSpeech:
        return jsonify({"text":result.translations[lang.split('-')[0]]})

    return jsonify({"text":"Recognition failed"})


if __name__ == '__main__':
    app.run(debug=True)
