"""
Example client for Sutra AI streaming API.

Demonstrates:
- Progressive answer refinement
- Real-time confidence updates
- Handling of streaming stages
"""

import asyncio
import json
import httpx


async def stream_query_simple(query: str, api_url: str = "http://localhost:8001"):
    """
    Simple streaming client - prints results as they arrive.
    
    Args:
        query: Question to ask
        api_url: Base URL of Sutra Hybrid API
    """
    url = f"{api_url}/sutra/stream/query"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream(
            "POST",
            url,
            json={"query": query, "max_concepts": 10}
        ) as response:
            print(f"\n🤔 Query: {query}")
            print("=" * 60)
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    try:
                        chunk = json.loads(data)
                        
                        # Print progress
                        stage = chunk.get('stage', 'unknown')
                        answer = chunk.get('answer', '')
                        confidence = chunk.get('confidence', 0.0)
                        paths = chunk.get('paths_found', 0)
                        is_final = chunk.get('is_final', False)
                        
                        # Stage indicator
                        if stage == 'initial':
                            print(f"\n⚡ Initial answer (1 path):")
                        elif stage == 'refining':
                            print(f"\n🔄 Refining... ({paths} paths):")
                        elif stage == 'consensus':
                            print(f"\n🎯 Consensus ({paths} paths):")
                        elif stage == 'complete':
                            print(f"\n✅ Final answer ({paths} paths):")
                        
                        # Answer
                        print(f"   {answer}")
                        print(f"   Confidence: {confidence:.2f}")
                        
                        if is_final:
                            print("\n" + "=" * 60)
                            break
                    
                    except json.JSONDecodeError:
                        pass


async def stream_query_with_callback(
    query: str,
    on_chunk,
    api_url: str = "http://localhost:8001"
):
    """
    Streaming client with callback for custom handling.
    
    Args:
        query: Question to ask
        on_chunk: Callback function called for each chunk
        api_url: Base URL of Sutra Hybrid API
    """
    url = f"{api_url}/sutra/stream/query"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream(
            "POST",
            url,
            json={"query": query, "max_concepts": 10}
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    try:
                        chunk = json.loads(data)
                        await on_chunk(chunk)
                        
                        if chunk.get('is_final'):
                            break
                    except json.JSONDecodeError:
                        pass


async def stream_query_collect_all(
    query: str,
    api_url: str = "http://localhost:8001"
) -> list:
    """
    Collect all streaming chunks into a list.
    
    Useful for analysis or replay.
    
    Args:
        query: Question to ask
        api_url: Base URL of Sutra Hybrid API
    
    Returns:
        List of all chunks received
    """
    chunks = []
    
    async def collect(chunk):
        chunks.append(chunk)
    
    await stream_query_with_callback(query, collect, api_url)
    return chunks


# Example usage
async def main():
    """Run example streaming queries."""
    
    # Example 1: Simple streaming
    print("\n" + "=" * 60)
    print("Example 1: Simple Streaming")
    print("=" * 60)
    await stream_query_simple("What is machine learning?")
    
    # Example 2: With custom callback
    print("\n" + "=" * 60)
    print("Example 2: Custom Callback")
    print("=" * 60)
    
    async def my_callback(chunk):
        stage = chunk['stage']
        conf = chunk['confidence']
        print(f"[{stage.upper()}] Confidence: {conf:.2f}")
    
    await stream_query_with_callback(
        "What is artificial intelligence?",
        my_callback
    )
    
    # Example 3: Collect all chunks
    print("\n" + "=" * 60)
    print("Example 3: Collect All Chunks")
    print("=" * 60)
    
    chunks = await stream_query_collect_all("What is deep learning?")
    print(f"Received {len(chunks)} chunks")
    print(f"Confidence progression: {[c['confidence'] for c in chunks]}")


if __name__ == "__main__":
    asyncio.run(main())
