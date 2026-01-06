"""
Streaming responses for better UX
User sees response as it's being generated instead of waiting
"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import asyncio

async def stream_response(answer: str):
    """
    Stream answer word by word
    
    Args:
        answer: Complete answer text
    
    Yields:
        JSON chunks with incremental text
    """
    words = answer.split()
    
    for i, word in enumerate(words):
        chunk = {
            "text": word + " ",
            "done": i == len(words) - 1
        }
        yield f"data: {json.dumps(chunk)}\\n\\n"
        await asyncio.sleep(0.05)  # Small delay between words

# In main.py, add this endpoint:
"""
@app.post("/api/rag-stream")
async def rag_stream(request: RagRequest):
    # Get answer from pipeline
    result = prometheus_pipeline(request.query, request.lang)
    
    # Stream the response
    return StreamingResponse(
        stream_response(result['answer']),
        media_type="text/event-stream"
    )
"""

# Frontend usage (Chat.jsx):
"""
const fetchStream = async (query, lang) => {
    const response = await fetch('http://localhost:8000/api/rag-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, language: lang })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let text = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                text += data.text;
                setTypingEffect(text);  // Update UI in real-time
            }
        }
    }
};
"""
