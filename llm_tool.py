import asyncio
import os
from fastapi import HTTPException
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

async def google_chat_completions(
    input: str,
    system_prompt: str = "",
    model: str = "gemini-2.0-pro-exp-02-05"
):
    try:
        google_client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=GOOGLE_API_KEY
        )
        
        response = google_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input}
            ],
            temperature=0.6,
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def groq_chat_completions(
    input: str,
    system_prompt: str = "",
    model: str = "deepseek-r1-distill-llama-70b-specdec"
):
    try:
        groq_client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        
        response = groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input}
            ],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
async def mistral_chat_completions(
    input: str,
    system_prompt: str = "",
    model: str = "mistral-large-latest"
):
    try:
        client = OpenAI(
            api_key=MISTRAL_API_KEY,
            base_url="https://api.mistral.ai/v1"
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input}
            ],
            temperature=0.6,
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# if __name__ == "__main__":
#     input = "What is the meaning of life?, print output in json format output as key and answer as value"
#     system_prompt = "The meaning of life is"
    
#     google_response = asyncio.run(google_chat_completions(input, system_prompt))
#     groq_response = asyncio.run(groq_chat_completions(input, system_prompt))
#     mistral_response = asyncio.run(mistral_chat_completions(input, system_prompt))
    
#     print(f"Google: {google_response}")
#     print(f"Groq: {groq_response}")
#     print(f"Mistral: {mistral_response}")