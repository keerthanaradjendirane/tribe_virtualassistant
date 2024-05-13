from flask import Flask, request, jsonify
import speech_recognition as sr
import pyttsx3
import pyjokes
import datetime
import pywhatkit
import re

app = Flask(__name__)

# Initialize speech recognition and text-to-speech engines
listener = sr.Recognizer()
engine = pyttsx3.init()

# Change voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # You can change the index to select a different voice

# Function to convert text to speech and return as JSON
def talk(text):
    engine.say(text)
    engine.runAndWait()
    return jsonify({'response': text})

# Function to fetch a joke and return as JSON
def get_joke():
    joke = pyjokes.get_joke()
    return jsonify({'joke': joke})

# Define NLP patterns for specific commands or questions
nlp_patterns = {
    r'call (.+)': lambda contact_name: make_call(contact_name),
    r'today\'s special food|today special food|food|special food here': lambda: talk("Today's special food is French onion soup, beef bourguignon, and crème brûlée."),
    r'breakfast menu|what do you have for breakfast|what can i have for breakfast|breakfast': lambda: talk("For breakfast, we have croissants, omelette du fromage, and pain au chocolat."),
    r'lunch menu|what do you have for lunch|what can i have for lunch|lunch': lambda: talk("For lunch, you can enjoy quiche Lorraine, salade niçoise, and coq au vin."),
    r'dinner menu|what do you have for dinner|what can i have for dinner|dinner': lambda: talk("For dinner, we recommend ratatouille, moules marinières, and boeuf en daube."),
    r'what do you have for desserts|desserts|snacks|snacks menu|snacks': lambda: talk("For dessert, we have tarte Tatin, profiteroles, and mille-feuille."),
    r'play (.+)': lambda song: (talk(f'playing {song}'), pywhatkit.playonyt(song)),
    r'what is the current time|time|current time|what is the time now|time now': lambda: talk(f'Current time is {datetime.datetime.now().strftime("%I:%M %p")}'),
    r'tell me a joke|say me a joke|joke': lambda: get_joke(),
    r'places to visit in auroville|places': lambda: talk("You can visit Matrimandir and Auroville Beach and so on."),
    r'nearby restaurants in auroville': lambda: talk("You can try Cafe Xtasi and Cafe Veloute."),
    r'nearby cafes in auroville': lambda: talk("You can try Cafe Xtasi and Cafe Veloute."),
    r'what can you do|i am bored': lambda: talk("i can help you with calling room service, providing you menu, telling you a joke, helping in finding the nearby restuarnts, and recomending you the places to visit"),
}

# Function to make a call (replace with actual call logic)
def make_call(contact_name):
    # Replace this with your actual call logic
    contacts = {
        'room service': '+919344413938',
        # Add more contacts as needed
    }
    phone_number = contacts.get(contact_name.lower(), None)
    if phone_number:
        talk("Calling " + contact_name)
        # Add call logic here (Twilio or other service)
        return jsonify({'response': f"Calling {contact_name}"})
    else:
        return jsonify({'response': "Sorry, I don't have a number for that contact."})

# Function to recognize speech input and respond accordingly using NLP patterns
def listen():
    try:
        with sr.Microphone() as source:
            print('Listening...')
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            print("Command:", command)

            # Check if any NLP pattern matches the command
            for pattern, action in nlp_patterns.items():
                match = re.match(pattern, command)
                if match:
                    args = match.groups()
                    return action(*args)

            # Default response if no NLP pattern matches
            return talk("Pardon")
    except sr.UnknownValueError:
        return talk("")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return talk("I'm sorry, there was an error processing your request.")

# Route to handle commands
@app.route('/process_command', methods=['POST'])
def process_command():
    data = request.json
    command = data['command']
    response = listen(command)
    return response

if __name__ == '__main__':
    app.run(debug=True)
