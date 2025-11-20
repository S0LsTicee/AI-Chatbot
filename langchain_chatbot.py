import os

from google.colab import userdata

os.environ["GOOGLE_API_KEY"] = "AIzaSyC4lF8qO_7e3snyux6O_Xp5gNQ9Dvndd8M"
os.environ["GOOGLE_API_KEY"] = userdata.get("GOOGLE_API_KEY")

os.environ.get("GOOGLE_API_KEY") == "AIzaSyC4lF8qO_7e3snyux6O_Xp5gNQ9Dvndd8M"

from typing import Annotated                      # Helps with type hints (optional but good practice)
from typing_extensions import TypedDict           # Helps us define data structures

from langgraph.graph import StateGraph, START, END    # The main graph components
from langgraph.graph.message import add_messages      # Handles message management
from langchain.chat_models import init_chat_model     # Connects to AI models

# Define what our chatbot will remember
class State(TypedDict):
    # This stores all the messages in our conversation
    # The `add_messages` part tells LangGraph to add new messages to the list
    # instead of replacing the whole list
    messages: Annotated[list, add_messages]

# Connect to Google's Gemini AI model
# "gemini-2.0-flash" is a fast and capable version of Google's AI
llm = init_chat_model("google_genai:gemini-2.0-flash")

# This function is the "brain" of our chatbot
def chatbot(state: State):
    """
    This function takes the conversation history and generates a response.

    How it works:
    1. Takes all the messages from the conversation so far
    2. Sends them to the AI model (Gemini)
    3. Gets back a response
    4. Returns the response in the format LangGraph expects
    """
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Step 1: Create a graph builder
graph_builder = StateGraph(State)

# Step 2: Add our chatbot function as a "node" in the graph
# The first part ("chatbot") is just a name we give it
# The second part (chatbot) is our actual function
graph_builder.add_node("languini", chatbot)

# Step 3: Define the flow: START → chatbot → END
graph_builder.add_edge(START, "languini")  # When conversation starts, go to chatbot
graph_builder.add_edge("languini", END)    # After chatbot responds, end this turn

# Step 4: Build the final graph
graph = graph_builder.compile()

# Function to send a message and get a response
def send_message(user_input: str):
    """
    Send a message to the chatbot and display the response.
    """
    print(f"User: {user_input}")

    # Send the message through our graph
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            response = value["messages"][-1].content
            print(f"Assistant: {response}")
    print("-" * 50)  # Separator line

# Test with a simple message
send_message("How can I get better at building AI agents?")

send_message("Can you explain what Python is in simple terms?")

send_message("I'm new to AI and chatbots. What should I learn next?")

send_message("Write a short poem about robots learning to code")

# Interactive chat session
print("🤖 Welcome to your chatbot!")
print("Type your messages below. Type 'quit' to exit.")
print("=" * 50)

try:
    while True:
        # Get user input
        user_input = input("\nYou: ")

        # Check if user wants to quit
        if user_input.lower() in ["quit", "exit", "q", "bye"]:
            print("Chatbot: Goodbye! Thanks for chatting! 👋")
            break

        # Send message to chatbot
        print("Chatbot: ", end="")
        for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
            for value in event.values():
                response = value["messages"][-1].content
                print(response)

except KeyboardInterrupt:
    print("\n\nChatbot: Goodbye! Thanks for chatting! 👋")
except:
    print("\n\nNote: Interactive input might not work in all environments.")
    print("If you see this message, try using the send_message() function instead!")
  
