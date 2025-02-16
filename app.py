import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load your personal data
with open("mumbere_darius_profile.json", "r") as file:
    personal_data = json.load(file)

# Directly set your API key here
api_key = "AIzaSyAN23PVrXsIBkYO43JVrXa69hdbRvBqkoY"  # Replace with your actual key

# Configure Gemini API
genai.configure(api_key=api_key)

# Initialize conversation history
conversation_history = []

# Function to generate AI responses with context
def ask_gemini(question, history):
    model = genai.GenerativeModel("gemini-pro")  # Use free-tier model if available

    # Build the prompt including conversation history and personal data
    prompt = f"Based on this information: {personal_data_to_string(personal_data)}\n\n"

    if history:
        prompt += "Conversation History:\n"
        for turn in history:
            prompt += f"User: {turn['user']}\nAI: {turn['ai']}\n"
    
    prompt += f"Question: {question}"

    response = model.generate_content(prompt)
    return response.text if response else "I don't know the answer."


def personal_data_to_string(data):
    # Convert personal data to a string, handling nested structures
    def flatten(d, parent_key="", sep="_"):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    items.extend(flatten({str(i): item}, new_key, sep=sep).items()) #handle lists by index
            else:
                items.append((new_key, v))
        return dict(items)
    
    flat_data = flatten(data)
    return "\n".join([f"{k}: {v}" for k, v in flat_data.items()])

# Flask API
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route("/ask", methods=["POST"])
def ask_question():
    user_question = request.json.get("question")
    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    answer = ask_gemini(user_question, conversation_history)

    # Update conversation history
    conversation_history.append({"user": user_question, "ai": answer})
    # Limit history length to avoid excessive context
    if len(conversation_history) > 5:  # Keep the last 5 exchanges
        conversation_history.pop(0)

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
