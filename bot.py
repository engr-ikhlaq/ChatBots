from flask import Flask, render_template, request, jsonify
import cohere
import requests

# Set up your Cohere API key
cohere_api_key = "B7YjT1Txj1drf1A5C90V0QQY2N7v5P5oR6AMgXiu"
co = cohere.Client(cohere_api_key)

# Flask App
app = Flask(__name__)


# Enhanced retrieval function
def retrieve_information(query):
    try:
        api_key = "AIzaSyBiYcHbl2BDtmKOg0aKbAJf9CivJVMRxAU"  # Replace with your Google API key
        cx = "AIzaSyBiYcHbl2BDtmKOg0aKbAJf9CivJVMRxAU"  # Replace with your Custom Search Engine ID
        search_api_url = f"https://www.googleapis.com/customsearch/v1"
        response = requests.get(search_api_url, params={
            'q': query,
            'key': api_key,
            'cx': cx
        })
        data = response.json()
        results = data.get('items', [])
        if results:
            return results[0]['title'] + ": " + results[0][
                'snippet']  # Return the title and snippet of the first result
        else:
            return 'No relevant information found.'
    except Exception as e:
        return f"Error retrieving information: {e}"


# Function to generate a response using RAG
def generate_response(user_input, context):
    try:
        # Retrieve relevant information
        retrieved_info = retrieve_information(user_input)

        # Generate response using Cohere
        prompt = f"""
        {context}
        {retrieved_info}
        User asked: {user_input}
        """
        response = co.generate(
            model='command',  # Replace with actual model name
            prompt=prompt,
            max_tokens=500,  # Increased token limit for more detailed responses
            temperature=0.7  # Controls the creativity of the response
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Error generating response: {e}"


# Advanced LangGraph for managing conversation states
class LangGraph:
    def __init__(self):
        self.state = "start"
        self.context = ""
        self.history = []

    def update_state(self, user_input):
        self.history.append(user_input)
        if "product" in user_input.lower():
            self.state = "product_info"
        elif "support" in user_input.lower():
            self.state = "support_info"
        else:
            self.state = "default"

        # Update context based on the state
        if self.state == "product_info":
            self.context = "Providing detailed product information."
        elif self.state == "support_info":
            self.context = "Assisting with support queries."
        else:
            self.context = "General conversation context."

    def get_context(self):
        return "\n".join(self.history)  # Provide full history for context


langgraph = LangGraph()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']

    if user_input.strip() == "":
        return jsonify({"response": "Please enter a message."})

    # Update conversation state
    langgraph.update_state(user_input)

    # Process the user input through the RAG system
    chatbot_response = generate_response(user_input, langgraph.get_context())

    return jsonify({"response": chatbot_response})


if __name__ == '__main__':
    app.run(debug=True)
