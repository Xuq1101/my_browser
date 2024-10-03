
import os
import aiohttp
import asyncio
from opendevin.core.logger import opendevin_logger as logger
from opendevin.core.schema import ActionType
from opendevin.events.observation import RagSearchOutputObservation

RAG_ENDPOINT = os.environ.get('RAG_ENDPOINT', 'http://127.0.0.1:3013/retrieve')

async def search(query):
    params = {
        'query': query,
        'top_n': 5,
    }
    headers = {'Content-Type': 'application/json'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(RAG_ENDPOINT, json=params, headers=headers, timeout=5) as response:
                if response.status != 200:
                    return {'response': ''}
                response_json = await response.json()
                # Remove duplicates from the context
                unique_context = list(dict.fromkeys(response_json['context']))
                return {'response': unique_context}
    except Exception as e:
        logger.debug(f'error in fetching - {query}: {e}')

async def rag_search(action) -> RagSearchOutputObservation:
    if action.action == ActionType.RAG_SEARCH:
        response = await search(action.query)
        return RagSearchOutputObservation(
            query=action.query,
            content=str(response['response']),
            context=response['response'],
        )
