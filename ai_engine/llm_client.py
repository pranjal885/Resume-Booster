#Your Python application is one person.
# Gemini is another person.
# llm_client.py is the telephone between them.

import os #reads environment variables such as GEMINI_API_KEY.
import json #converts Gemini's JSON response from text into Python objects.
import re #regular expressions; used to remove ```json code fences.
from dotenv import load_dotenv #loads variables from your .env file.

# Ensure environment variables from .env are loaded
load_dotenv(override=True)
#load_dotenv() = load .env values in python environment.
#override=True = allow those .env values to replace existing environment variables.

# Recommended default model for fast, high-quality reasoning
DEFAULT_GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.6-flash')
#os.environ allows Python to access environment variables.
#os.environ.get('GEMINI_MODEL', ...) means Look for an environment variable called GEMINI_MODEL.
#DEFAULT_GEMINI_MODEL stores the Gemini model to be used. It first reads GEMINI_MODEL from the environment, and if it is not defined, it uses gemini-3.6-flash as the default model.
#First look for GEMINI_MODEL in the environment. If it isn't there, use gemini-3.6-flash.


#We chose Gemini 3.6 Flash because our application needs multiple AI operations with fast responses.
#It provides a good balance between response quality and speed, and we also kept the model configurable through the environment variable.

def is_ai_available():
    """
    Checks if the GEMINI_API_KEY environment variable is configured.
    Returns True if an API key is present and not a dummy placeholder, False otherwise.
    """
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    #It retrieves the API key from the environment.
    if not api_key or api_key == 'your_gemini_api_key_here':
        #if:there is no key, Or the key is just the placeholder → AI is considered unavailable.
        return False
    return True

def get_llm_client():
    #This function actually creates the Gemini client.
    """
    Initializes and returns a Google Gemini client if available.
    Returns None if GEMINI_API_KEY is missing or invalid.
    """
    if not is_ai_available():
        return None
    #Again, it avoids trying to initialize Gemini when there is no key.
    #So if there is no API key, we don't even try to connect to Gemini.
        
    try:
        from google import genai #This imports Google's Gemini SDK.
        #This gives our Python program access to Google's Gemini API functionality.
        api_key = os.environ.get('GEMINI_API_KEY', '').strip()
        client = genai.Client(api_key=api_key) #This creates the Gemini client using your API key.
        #Think of the client as the thing that allows our Python application to communicate with Gemini.
        return client #Now another function can receive this client and use it to send requests.
    except Exception as e:
        print(f"[AI ENGINE WARNING] Failed to initialize Gemini Client: {e}")
        return None

def call_llm(prompt, system_instruction=None, json_output=False, model_name=None):
    #This is the main reusable Gemini function.
    #Instead of every AI feature writing its own Gemini API code, they can simply call:
# call_llm(...)
# That's excellent architecture.
#You can think of call_llm() as:
#"Send something to Gemini and get the AI's response."

# Think of it as:

#                     ┌─────────────────┐
# Resume Analyzer ───►│                 │
# Bullet Improver ───►│   call_llm()    │───► Gemini
# Summary Generator ─►│                 │
# Chatbot ───────────►│                 │
#                     └─────────────────┘
# One central function handles communication with Gemini.

    """
    Sends a prompt to the Google Gemini LLM API and returns the text response.
    
    Parameters:
    - prompt (str): The main prompt text containing resume/job context and instructions.
    - system_instruction (str, optional): System role or guidelines for the AI model.
    - json_output (bool): If True, requests structured JSON output from Gemini.
    - model_name (str, optional): The Gemini model to use (default: GEMINI_MODEL env var or 'gemini-2.0-flash').
    
    Returns:
    - str or None: Raw response text from Gemini, or None if the call fails/API unavailable.
    """
    if not is_ai_available():
        return None

    client = get_llm_client()
    if not client:
        return None
        
    target_model = model_name or os.environ.get('GEMINI_MODEL', DEFAULT_GEMINI_MODEL)
        
    try:
        from google.genai import types
        #We import types from the Google Gemini SDK so that we can create GenerateContentConfig,
        # which allows us to configure the Gemini request, such as providing system instructions and requesting JSON output.
        
        # Build generation configuration
        config_kwargs = {} #{} means an empty Python dictionary.
        if system_instruction:
            config_kwargs['system_instruction'] = system_instruction
            #Check whether we have a system instruction
            # if yes adds it to our dictionary.
            #Now:
# config_kwargs = {
#     'system_instruction': 'You are an expert resume coach.'
# }
        if json_output:
            #Check whether JSON output is required

            config_kwargs['response_mime_type'] = "application/json"
                       #adds another setting.
            # Now the dictionary becomes something like:
            # config_kwargs = {
            #     'system_instruction': 'You are an expert resume coach.',
            #     'response_mime_type': 'application/json'
            # }
            
        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
        #types.GenerateContentConfig(...)
        #This creates a Gemini configuration object.
        #The ** means:
        #Take all the key-value pairs from this dictionary and pass them as arguments.
        #This line converts our optional configuration dictionary into a Gemini GenerateContentConfig object,
        #but only if the dictionary contains settings; otherwise it sets config to None.
        response = client.models.generate_content(
            #client is our Gemini connection/client.
            #client.models.generate_content()
            #This is Google's function for asking Gemini to generate a response.
            model=target_model,
            contents=prompt,
            config=config #This gives Gemini the optional settings we prepared earlier.
        )
        
        if response and response.text:
            return response.text.strip()
        return None
    #Did we get a response?
#         AND
# Does that response contain text?
        
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str.upper() or "QUOTA" in err_str.upper():
            print(f"[AI ENGINE WARNING] Gemini API quota limit reached (429 ResourceExhausted). Falling back to deterministic engine.")
        else:
            print(f"[AI ENGINE ERROR] Gemini API call failed: {e}")
        return None
    #We have implemented exception handling around the Gemini API call.
    # If a 429 quota error occurs, the system logs the issue and returns None, allowing the application to fall back to its deterministic engine instead of crashing.

def call_llm_json(prompt, system_instruction=None, model_name=None):
    #main job of this function : Call Gemini and get the answer in JSON format.
    #Why do we need this function?
# Earlier we had:
# call_llm()
# which gets a normal text response from Gemini.
# But some features of our project need Gemini to return structured JSON.


    """
    Helper function to call Gemini and safely parse the JSON response.
    
    Returns:
    - dict/list or None: Parsed JSON object, or None if API call fails or JSON is malformed.
    """
    raw_response = call_llm(
        prompt=prompt,
        system_instruction=system_instruction,
        json_output=True, #Call our call_llm() function and tell it that we want JSON output.
        model_name=model_name
    )
    
    if not raw_response:
        return None
        
    # Clean possible markdown code fences (e.g. ```json ... ```)
    cleaned_json = raw_response #This simply makes a copy of Gemini's response.
    if "```" in cleaned_json:

#     Gemini sometimes puts JSON inside a Markdown code block:
# ```json
# {
#    "score": 85
# }


        # Match inside code blocks if present
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', cleaned_json, re.DOTALL)
        #Find the actual JSON content inside the code block.
        if match:
            cleaned_json = match.group(1).strip()
            #This takes the actual JSON content that was found and removes unnecessary spaces/newlines around it.
            
    try:
        #Try to execute this code. If something goes wrong, don't crash the program; handle the error below.
        return json.loads(cleaned_json)
        #json.loads() converts a JSON-formatted text string into a Python dictionary/list.
    except json.JSONDecodeError as err:
#         What if Gemini gives us invalid JSON?
# For example:
# {"score": 85, "skills": ["Python", "SQL"
# There is a missing ] and }.
# Then json.loads() cannot convert it.
# Instead of the whole application crashing, Python catches that specific error here.
# err contains information about what went wrong.
        print(f"[AI ENGINE WARNING] Failed to parse JSON response from Gemini: {err}\nRaw text: {raw_response[:200]}")
        #It also prints the first 200 characters of Gemini's original response:
# raw_response[:200]
# This is useful for debugging because we can see what Gemini actually returned.
        return None
