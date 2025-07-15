import os
import json
import time
# from openai import OpenAI # Commented out as we are switching to Gemini
import google.generativeai as genai # Uncommented for Google Gemini API

def get_llm_response(prompt: str, api_key: str, provider: str = "gemini", model: str = None) -> str:
    """
    Sends a prompt to the specified LLM provider (OpenAI or Gemini) and returns the response.

    Args:
        prompt (str): The prompt text to send to the LLM.
        api_key (str): The API key for the chosen LLM provider.
        provider (str): The LLM provider to use ('openai' or 'gemini'). Defaults to 'gemini'.
        model (str, optional): The specific model name to use. If None, uses default for provider.

    Returns:
        str: The LLM's response, expected to be a JSON string.

    Raises:
        ValueError: If an unsupported provider is specified or API key is missing.
        Exception: For API call errors.
    """
    if not api_key:
        raise ValueError(f"API key is missing for LLM provider: {provider}")

    if provider == "openai":
        # This block is now effectively disabled if you're primarily using Gemini
        # from openai import OpenAI # Re-import if you uncomment this block
        # if model is None:
        #     model = "gpt-3.5-turbo-0125" # Recommended latest GPT-3.5 Turbo model
        # try:
        #     client = OpenAI(api_key=api_key) 
        #     response = client.chat.completions.create(
        #         model=model,
        #         messages=[
        #             {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
        #             {"role": "user", "content": prompt}
        #         ],
        #         response_format={"type": "json_object"},
        #         temperature=0.0
        #     )
        #     return response.choices[0].message.content
        # except Exception as e:
        #     print(f"An error occurred with OpenAI API: {e}")
        #     raise
        pass # Placeholder if OpenAI block is commented out

    elif provider == "gemini":
        genai.configure(api_key=api_key)
        if model is None:
            model = "gemini-1.5-flash" # Recommended latest Gemini Flash model

        try:
            client = genai.GenerativeModel(model_name=model)
            
            # For structured output, we instruct the model in the prompt
            # and set response_mime_type in generation_config.
            response = client.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json", # Request JSON output
                    "temperature": 0.0 # Keep temperature low for factual extraction
                }
            )
            # Gemini's response for JSON output is typically in response.text
            return response.text
        except Exception as e:
            print(f"An unexpected error occurred with Gemini API: {e}")
            raise

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Choose 'openai' or 'gemini'.")

if __name__ == '__main__':
    # Example usage (for testing this module independently)
    from dotenv import load_dotenv
    load_dotenv() # Load API keys from .env

    print("--- Testing Google Gemini LLM Client ---")
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        test_prompt_invoice = """
        Extract the invoice number, date, vendor name, total amount, currency, and a brief summary.
        Provide the output in JSON format.
        Invoice Text:
        ABC Corp.
        Invoice #INV-2023-045
        Date: 2023-10-26
        Total Due: $1250.00 USD
        For services rendered.
        """
        try:
            print("Sending invoice prompt to Gemini...")
            response_gemini = get_llm_response(test_prompt_invoice, google_key, provider="gemini")
            print("Gemini Response (Invoice):")
            print(json.dumps(json.loads(response_gemini), indent=2))
        except Exception as e:
            print(f"Gemini test failed: {e}")
    else:
        print("Google Gemini API key not found in .env. Skipping Gemini test.")

    # You can uncomment and test OpenAI if you switch back, but for now it's commented out
    # print("\n--- Testing OpenAI LLM Client (Currently Commented Out) ---")
    # openai_key = os.getenv("OPENAI_API_KEY")
    # if openai_key:
    #     test_prompt_contract = """
    #     Extract the contract title, parties, effective date, and a brief overall summary.
    #     Provide the output in JSON format.
    #     Contract Text:
    #     SOFTWARE LICENSE AGREEMENT
    #     Between: Tech Innovators Inc. and Global Solutions Ltd.
    #     Effective Date: January 1, 2024
    #     This agreement grants a non-exclusive license for software usage.
    #     """
    #     try:
    #         print("Sending contract prompt to OpenAI...")
    #         response_openai = get_llm_response(test_prompt_contract, openai_key, provider="openai")
    #         print("OpenAI Response (Contract):")
    #         print(json.dumps(json.loads(response_openai), indent=2))
    #     except Exception as e:
    #         print(f"OpenAI test failed: {e}")
    # else:
    #     print("OpenAI API key not found in .env. Skipping OpenAI test.")
