import json
import aiohttp
from typing import Dict, Any
from config import Config
import asyncio
from functools import wraps

def with_retry(max_retries: int = Config.MAX_RETRIES):
    """Decorator to add retry logic to async functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
            raise last_exception
        return wrapper
    return decorator

class OpenAIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass

async def analyze_repository(prompt: str) -> Dict[str, Any]:
    """
    Send a prompt to OpenAI API and get the analysis response.
    
    Args:
        prompt (str): The prompt to send to OpenAI
        
    Returns:
        Dict[str, Any]: The response from OpenAI containing the analysis
        
    Raises:
        OpenAIError: If there's an error with the OpenAI API
    """
    Config.validate()
    
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        **Config.get_openai_config(),
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant specialized in analyzing codebases and providing structured summaries."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    @with_retry()
    async def make_request():
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    Config.OPENAI_API_URL,
                    headers=headers,
                    json=data,
                    timeout=Config.TIMEOUT
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    if 'choices' not in result or not result['choices']:
                        raise OpenAIError("Invalid response format from OpenAI API")
                        
                    content = result['choices'][0]['message']['content']
                    return json.loads(content)
            except aiohttp.ClientError as e:
                raise OpenAIError(f"HTTP error occurred: {str(e)}")
            except json.JSONDecodeError as e:
                raise OpenAIError(f"Failed to parse OpenAI response: {str(e)}")
            except Exception as e:
                raise OpenAIError(f"Unexpected error: {str(e)}")
    
    return await make_request() 