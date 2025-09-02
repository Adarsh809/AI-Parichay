---
title: AI-Parichay
app_file: app.py
sdk: gradio
sdk_version: 5.44.1
---
# AI-Parichay: Next-Gen Introduction
## Powered by RAG and Agentic AI

This project creates a personal AI chatbot that acts as a digital version of me. It uses Google's Gemini Pro model via the OpenAI client library to conduct conversations, answer questions based on personal documents (Resume, LinkedIn profile), and interact with external tools to perform specific actions. The application is served through a user-friendly web interface created with Gradio.


---

## Features

-   **Conversational AI**: Powered by Google's `gemini-2.5-flash` model for natural and engaging conversations.
-   **Persona-Based**: The chatbot adopts a specific persona, using provided documents to answer questions accurately and stay in character.
-   **Document-Aware**: Reads and synthesizes information from PDF files (`Resume.pdf`, `linkedin.pdf`) and text files (`summary.txt`) to build its knowledge base.
-   **Tool Integration (Function Calling)**: The AI can decide to call predefined Python functions to:
    -   Record a user's contact information (`record_user_details`).
    -   Log questions it was unable to answer (`record_unknown_question`).
-   **Real-time Notifications**: Uses the [Pushover](https://pushover.net/) service to send instant notifications whenever a tool is used (e.g., when a new user leaves their email).
-   **Interactive Web UI**: Built with Gradio to provide a simple and effective chat interface.
-   **Secure Configuration**: Manages API keys and sensitive tokens using a `.env` file.

---

## How It Works

The application's logic is encapsulated within the `Me` class.

1.  **Initialization**: When the application starts, the `Me` class is instantiated. It loads the content from the PDF and text files in the `data/` directory into memory. It also initializes the `OpenAI` client, configured to point to Google's Generative Language API endpoint for Gemini.

2.  **System Prompt**: For every conversation, a dynamic system prompt is generated. This prompt instructs the AI on its persona, its goals (e.g., be helpful, try to get user's email), and provides all the loaded document content as context.

3.  **Chat Interaction**:
    -   The user sends a message through the Gradio interface.
    -   The `chat` method constructs a message list, including the system prompt, conversation history, and the new user message.
    -   This list is sent to the Gemini API.

4.  **Tool Execution**:
    -   The Gemini model may decide that it needs to call a function to fulfill the user's request (e.g., the user provides an email).
    -   If so, the API response will include `tool_calls` instead of a final text message.
    -   The `handle_tool_call` method parses these calls, executes the corresponding Python function (e.g., `record_user_details`), and sends the function's return value back to the model.
    -   The model then uses this result to generate its final, user-facing response.

5.  **Response Generation**: The final response from the model is streamed back to the Gradio interface for the user to see.

---

## Project Structure

```
.
├── data/
│   ├── linkedin.pdf         # Your LinkedIn profile saved as a PDF
│   ├── Resume.pdf           # Your resume/CV in PDF format
│   └── summary.txt          # A brief summary of your background
├── .env                     # File for environment variables (API keys)
├── app.py                   # Main application script
└── requirements.txt         # Python dependencies
```

---

## Setup and Installation

### Prerequisites

-   Python 3.8 or higher
-   A Google AI Studio API key for Gemini.
-   A Pushover account and API tokens (optional, for notifications).

### Step-by-Step Guide

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Adarsh809/AI-Parichay.git
    cd AI-Parichay
    ```

2.  **Create a Virtual Environment**
    It's recommended to use a virtual environment to manage dependencies.
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**
    Create a `requirements.txt` file with the following content:
    ```txt
    requests
    pypdf
    gradio
    python-dotenv
    openai
    ```
    Then, install the packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a file named `.env` in the root of the project and add your API keys.
    ```ini
    # .env
    GEMINI_API_KEY="your_google_ai_studio_api_key"
    PUSHOVER_TOKEN="your_pushover_app_token"
    PUSHOVER_USER="your_pushover_user_key"
    ```

5.  **Add Your Data**
    Place your personal documents in the `data/` directory. Ensure the filenames match those in `app.py` (`linkedin.pdf`, `Resume.pdf`, `summary.txt`).

---

## Usage

To run the chatbot, execute the `app.py` script from your terminal:

```bash
python app.py
```

Gradio will start a local web server. You will see a URL in the terminal (usually `http://127.0.0.1:7860`). Open this URL in your web browser to start chatting with your AI persona.

---

## Customization

This project is designed to be easily adapted.

-   **Change the Persona**: In the `Me` class `__init__` method, change the `self.name` attribute to your name.
    ```python
    def __init__(self):
        # ...
        self.name = "Your Name" # Change this
        # ...
    ```
-   **Modify the Behavior**: Edit the `system_prompt` method to change the chatbot's instructions, tone, or goals.
-   **Add New Tools**:
    1.  Define a new Python function that performs the desired action.
    2.  Create a corresponding JSON schema that describes the function, its purpose, and its parameters for the Gemini model.
    3.  Add the new function and its schema to the `tools` list.
    4.  Update `handle_tool_call` if any special logic is needed.

---
