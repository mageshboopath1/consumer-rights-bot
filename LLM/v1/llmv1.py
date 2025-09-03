import os
import sys
import json
import requests

def get_llm_response(prompt: str, model_name: str) -> str:
    """
    Sends a prompt to a local Ollama server and returns the generated text.

    Args:
        prompt (str): The final, formatted prompt from the RAG core.
        model_name (str): The name of the Ollama model to use (e.g., 'llama3').

    Returns:
        str: The generated response from the LLM.
    """
    # The URL for the local Ollama server's generate endpoint
    url = "http://localhost:11434/api/generate"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False  # We want the full response at once
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        
        # Extract the response from the Ollama payload
        generated_text = data.get('response', '')
        
        if not generated_text:
            raise ValueError("Ollama response was empty.")
            
        return generated_text

    except requests.exceptions.ConnectionError as e:
        print("Error: Could not connect to Ollama server.", file=sys.stderr)
        print("Please ensure Ollama is running and the model is downloaded.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, ValueError) as e:
        print(f"Failed to parse Ollama response: {e}", file=sys.stderr)
        print("Response:", response.text, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Both a prompt and an Ollama model name must be provided.", file=sys.stderr)
        print("Usage: python llm_container.py \"<your final prompt>\" <model_name>", file=sys.stderr)
        sys.exit(1)

    # The last argument is the model name
    model = sys.argv[-1]
    # The rest of the arguments form the prompt
    final_prompt = " ".join(sys.argv[1:-1])
    
    # Get the LLM's response
    llm_response = get_llm_response(final_prompt, model)
    
    # Print the response to standard output for the next component (or user)
    print(llm_response)