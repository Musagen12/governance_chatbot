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
    'from': 'en',  # English as the source language
    'to': ['sw']   # Swahili as the target language
}

headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

def convert_to_swahili(text: List[dict]):
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
        if isinstance(response, list) and all('translations' in item for item in response):
            # Extract the translations
            translations = [item['translations'][0]['text'] for item in response]
            return translations  # Return all translations as a list
        else:
            raise ValueError("Unexpected response format or missing 'translations' key")

    except Exception as e:
        print(f"Error occurred in convert_to_swahili: {e}")  # More context in error message
        raise

# Sample usage for testing
# text = [{'text': 'Hello, how are you?'}]
# result = convert_to_swahili(text)
# print(result)
