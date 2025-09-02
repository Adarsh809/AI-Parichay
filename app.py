import os
import json
import requests
from pypdf import PdfReader
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)

# Define tool functions as they are outside the class
def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )

def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

# Tool JSON schemas
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]

class Me:
    """
    A class representing the chat bot's persona and logic.
    """
    def __init__(self):
        """
        Initializes the chat bot, loading persona data and setting up the Gemini client.
        """
        # Configure the OpenAI client to use the Gemini API endpoint
        self.gemini = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.name = "Adarsh"
        
        # Load data from PDF
        reader1 = PdfReader("data/linkedin.pdf")
        self.linkedin = "".join(page.extract_text() or "" for page in reader1.pages)
        
        # Load data from Resume
        reader2 = PdfReader("data/Resume.pdf")
        self.resume = "".join(page.extract_text() or "" for page in reader2.pages)
        
        # Load summary from text file
        with open("data/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

    def handle_tool_call(self, tool_calls):
        """
        Executes tool calls requested by the language model.
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results
    
    def system_prompt(self):
        """
        Generates the dynamic system prompt for the chat bot.
        """
        prompt = (
            f"You are acting as {self.name}. You are answering questions on {self.name}'s website, "
            "particularly questions related to {self.name}'s career, background, skills and experience. "
            "Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. "
            "You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. "
            "Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
            "If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. "
            "If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "
        )
        prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n## Resume:\n{self.resume}\n\n"
        prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return prompt
    
    def chat(self, message, history):
        """
        The main chat loop for handling user messages and model responses.
        """
        # The history needs to be reformatted for Gemini, as it requires alternating user/model roles.
        # This implementation simplifies the process by rebuilding the list.
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            # Use the Gemini model name
            response = self.gemini.chat.completions.create(
                model="gemini-2.5-flash",
                messages=messages,
                tools=tools
            )
            
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content

# Main entry point of the application
if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat, type="messages").launch()