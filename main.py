from flask import Flask, request, jsonify
from flask_cors import CORS
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://sensitivestability.com"}})

# Define symptoms and triggers
SYMPTOMS = {
    "Fear of Abandonment": False,
    "Jealousy": False,
    "Anxiety": False,
    "Mood Swings": False,
    "Emptiness": False,
    "Lack of Self": False,
    "Suicidal Ideation": False,
    "Self-harm/Addictions": False,
    "Unstable Relationships": False,
    "Rage/Anger": False,
    "Paranoia/Dissociation": False,
    "Destructive Behavior": False,
    "Impulsivities": False
}

TRIGGERS = [
    "Feeling Unheard/Ignored/Unimportant",
    "Feeling Judged/Criticized/Challenged", "Feeling 'Not Good Enough'",
    "Feeling Compared to Others", "Expectation vs Reality Failure",
    "Being Alone", "Feeling Rejected", "Feeling Overwhelmed",
    "Feeling Hopeless/Threatened", "Thinking of the Past", "F.E.A.R.",
    "Feeling Disrespected", "Feeling Wronged/Unfair", "Lack of Purpose"
]


# Home route for testing if the app is running
@app.route('/')
def home():
    return "Flask app is running on Replit with the full code!"


@app.route('/ask_symptoms', methods=['GET'])
def ask_symptoms():
    return jsonify(list(SYMPTOMS.keys()))


@app.route('/ask_triggers', methods=['POST'])
def ask_triggers():
    data = request.get_json() or {}
    selected_symptoms = data.get("selected_symptoms", [])
    symptom_triggers = {}

    for symptom in selected_symptoms:
        if symptom in SYMPTOMS:
            symptom_triggers[symptom] = TRIGGERS

    return jsonify(symptom_triggers)


@app.route('/generate_symptom_map', methods=['POST'])
def generate_symptom_map():
    data = request.get_json() or {}
    symptom_triggers = data.get("symptom_triggers", {})

    if not symptom_triggers:
        return jsonify({"error": "No symptoms provided"}), 400

    symptoms = list(symptom_triggers.keys())
    triggers = list(
        set(trigger for trigger_list in symptom_triggers.values()
            for trigger in trigger_list))

    fig, ax = plt.subplots()
    fig.set_size_inches(14, 14)

    num_symptoms = len(symptoms)
    num_triggers = len(triggers)
    angle_symptoms = np.linspace(0, 2 * np.pi, num_symptoms, endpoint=False)
    angle_triggers = np.linspace(0, 2 * np.pi, num_triggers, endpoint=False)
    radius_symptoms = 2
    radius_triggers = 3

    symptom_positions = [(radius_symptoms * np.cos(angle),
                          radius_symptoms * np.sin(angle))
                         for angle in angle_symptoms]
    trigger_positions = [(radius_triggers * np.cos(angle),
                          radius_triggers * np.sin(angle))
                         for angle in angle_triggers]

    for pos, symptom in zip(symptom_positions, symptoms):
        ax.text(pos[0],
                pos[1],
                symptom,
                ha='center',
                va='center',
                bbox=dict(facecolor='red', alpha=0.5))

    for pos, trigger in zip(trigger_positions, triggers):
        ax.text(pos[0],
                pos[1],
                trigger,
                ha='center',
                va='center',
                bbox=dict(facecolor='blue', alpha=0.5))

    for symptom, trigger_list in symptom_triggers.items():
        symptom_index = symptoms.index(symptom)
        for trigger in trigger_list:
            if trigger in triggers:
                trigger_index = triggers.index(trigger)
                ax.plot([
                    symptom_positions[symptom_index][0],
                    trigger_positions[trigger_index][0]
                ], [
                    symptom_positions[symptom_index][1],
                    trigger_positions[trigger_index][1]
                ], 'k-')

    plt.axis('off')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.read()).decode('utf8')
    plt.close()

    return jsonify({'image': img_base64})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)