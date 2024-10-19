import requests, uuid, json
from dotenv import load_dotenv
from typing import List
import os

load_dotenv()

key = os.getenv("TRANSLATOR-KEY")
endpoint = os.getenv("TRANSLATOR_ENDPOINT")
location = os.getenv("RESOURCE-LOCATION")

path = '/translate'
constructed_url = endpoint + path

params = {
    'api-version': '3.0',
    'from': 'sw',  # Swahili as the source language
    'to': ['en']   # English as the target language
}

headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

def convert_to_english(text: List[dict]):
    try:
        # Send POST request
        request = requests.post(constructed_url, params=params, headers=headers, json=text)

        # Check for request status code
        if request.status_code != 200:
            raise Exception(f"Request failed with status code {request.status_code}: {request.text}")

        # Get response JSON
        response = request.json()
        print("Response from API:", response)  # Debugging output

        # Ensure the response contains the expected structure
        if isinstance(response, list) and len(response) > 0:
            translations = []
            for item in response:
                if isinstance(item, dict) and 'translations' in item:
                    # Loop through each translation
                    for translation in item['translations']:
                        if isinstance(translation, dict) and 'text' in translation:
                            translations.append(translation['text'])  # Append the translated text
                else:
                    raise ValueError("Unexpected response format")
            return translations  # Return all translations as a list
        else:
            raise ValueError("Expected response to be a non-empty list")

    except Exception as e:
        print(f"Error occurred in convert_to_english: {e}")  # More context in error message
        raise

# Sample usage for testing
# text = [{'text': 'katiba ni nini'}]
# result = convert_to_english(text)
# print(result)
