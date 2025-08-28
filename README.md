# AI powered server setup script generator

A Flask-based web application that generates a Bash script to carry out user-specified tasks on Ubuntu server by prompting an LLM.

---

## Prerequisites

- Python 3.8 or higher  
- Flask library  
- An Ubuntu-based system (or compatible) for running the generated script
- OpenAI sdk version 0.28 (**very important, later versions will not work**)  
- An openrouter (or any OpenAI sdk compatible API) API key

---

## Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/ananth-2022/ai-auto-script-generation.git
   ```

2. (Optional) Create and activate a virtual environment (use ```python3``` on mac/linux  
   ```bash
   python -m venv venv
   ```
3. Activate venv (make sure to deactivate when you are done)
   ```bash
   # on mac/linux
   source venv/bin/activate
   # on windows cmd
   venv\Scripts\activate.bat
   # on windows powershell
   .\venv\Scripts\Activate.ps1
   # to deactivate on mac/linux/powershell
   deactivate
   # to deactivate on cmd
   venv\Scripts\deactivate.bat
   ``` 

4. Install Python dependencies  
   ```bash
   pip install Flask openai==0.28
   ```
5. Create the .env file
   ```
   OPENAI_API_KEY="your api key"
   OPENROUTER_API_BASE="https://api.openai.com/v1"
   ```

---

## Usage

0. Edit the LLM prompt by changing the prompt variable in the ```generate_script()``` function
1. Start the Flask application  
   ```bash
   python app.py
   ```
2. Open your browser and navigate to  
   ```
   http://127.0.0:5000
   ```
3. Type required tasks into the textarea or upload a text file. (You can describe any additional instructions in plain english)
4. Click Download to retrieve the generated Bash script.  
5. Transfer `test_script.sh` to your Ubuntu server, make it executable, and run it:  
   ```bash
   chmod +x test_script.sh
   ./test_script.sh
   ```
   or if you have docker installed, you can test it with a local test container by running
   ```bash
   chmod +x test_script.sh
   python tester.py
   ```   

---

## Project Structure

- **app.py**  
  Flask application handling user input and script generation.

- **templates/index.html**  
  Frontend form for listing desired packages.

- **tester.py**  
  Testing with a local docker container.

---
