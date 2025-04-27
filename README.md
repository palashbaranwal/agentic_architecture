# Math Agent Chrome Extension

This project is a modular, agentic math problem solver that connects a Chrome extension frontend to a Python backend. The backend uses an agentic architecture with four main components: **Perceive, Memory, Decision, and Action**. Users can enter math problems (and a Gemini API key if needed) in the extension, and receive answers powered by your AI agent.

---

Youtube Demo - https://youtu.be/gpT0NJ1UFFg  

## Table of Contents

1. [Features](#features)  
2. [Architecture Overview](#architecture-overview)  
3. [Setup Instructions](#setup-instructions)  
    - [Python Backend](#python-backend)  
    - [Chrome Extension](#chrome-extension)  
4. [How It Works](#how-it-works)  
5. [Agentic Architecture Explained](#agentic-architecture-explained)  
6. [Usage](#usage)  
7. [Troubleshooting](#troubleshooting)  
8. [Contributing](#contributing)  
9. [License](#license)  

---

## Features

- Solve math problems from your browser using a Chrome extension
- Modular agentic backend with clear separation of concerns
- Optional Gemini API key support for advanced reasoning
- Clean, modern UI
- Easy to extend and maintain

---

## Architecture Overview

- **Frontend:** Chrome extension (popup) for user input and result display
- **Backend:** Python Flask server running the agentic math solver
- **Agentic Core:** Four main components—Perceive, Memory, Decision, Action—each with a clear responsibility

---

## Setup Instructions

### 1. Python Backend

**a. Install dependencies:**
```bash
pip install flask flask-cors
```

**b. Project structure:**
```
S6_Asgn/
│
├── flask_server.py # Main backend server (contains agent logic)
├── perceive.py # Perceive component
├── memory.py # Memory component
├── decision.py # Decision component
├── action.py # Action component
├── models.py # Pydantic models (if used)
└── other files ...
```

**c. Start the backend:**
```bash
python flask_server.py
```
By default, the server runs on `http://localhost:5000`.

---

### 2. Chrome Extension

**a. Project structure:**
```
chrome_extension/
│
├── manifest.json
├── popup.html
├── popup.js
└── icons
```

**b. Load the extension:**
1. Go to `chrome://extensions/` in Chrome.
2. Enable "Developer mode".
3. Click "Load unpacked" and select the `chrome_extension` folder.

---

## How It Works

1. **User enters a math problem (and optionally a Gemini API key) in the extension popup.**
2. **The extension sends the problem and key to the Flask backend via HTTP POST.**
3. **The backend instantiates the agent, passing the problem and Gemini key.**
4. **The agent processes the problem using its four core components:**
    - **Perceive:** Parses and interprets the input.
    - **Memory:** Stores and retrieves relevant information.
    - **Decision:** Determines the best course of action.
    - **Action:** Executes the chosen operation (e.g., calculation, reasoning).
5. **The result is returned to the extension and displayed to the user.**

---

## Agentic Architecture Explained

The backend agent is designed around four modular components:

### 1. **Perceive**
- **Role:** Receives and interprets user input.
- **Responsibilities:**  
  - Parses mathematical expressions.
  - Understands user commands.
  - Prepares data for further processing.

### 2. **Memory**
- **Role:** Stores and retrieves information.
- **Responsibilities:**  
  - Maintains calculation history.
  - Stores error patterns or user preferences.
  - Provides context for decision-making.

### 3. **Decision**
- **Role:** Chooses the best action based on input and memory.
- **Responsibilities:**  
  - Selects the appropriate mathematical operation.
  - Verifies calculations and checks consistency.
  - Handles errors and fallback logic.

### 4. **Action**
- **Role:** Executes the chosen operation.
- **Responsibilities:**  
  - Performs calculations (add, subtract, multiply, etc.).
  - Executes reasoning steps.
  - Returns results to the user.

**This separation makes the agent easy to extend, test, and maintain.**

---

## Usage

1. **Start the backend server:**  
   `python flask_server.py`
2. **Load the Chrome extension.**
3. **Click the extension icon, enter your math problem (and Gemini key if needed), and click "Solve".**
4. **View the result instantly in the popup!**

---

## Troubleshooting

- **"Could not connect to backend":**  
  Make sure the Flask server is running and accessible at `http://localhost:5000`.
- **"Invalid expression or error in calculation":**  
  Ensure you are entering a valid math expression (e.g., `2 + 3 * 4`).
- **Gemini API errors:**  
  Double-check your Gemini API key and network connection.

---

## Contributing

Contributions are welcome! Please open issues or pull requests for improvements, bug fixes, or new features.

---

## License

[MIT License](LICENSE)

---

Let me know if you want to add more details, usage examples, or diagrams!