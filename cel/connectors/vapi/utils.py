import time


def create_chunk_response(id: str, text: str = None):
  res = {
      "id": id,
      "choices": [
          {
              "delta": {
                  "content": text,
                  "function_call": None,
                  "role": None,
                  "tool_calls": None
              },
              "finish_reason": "stop" if text is None else None,
              "index": 0,
              "logprobs": None
          }
      ],
      "created": int(time.time()),
      "model": "gpt-3.5-turbo-0125",
      "object": "chat.completion.chunk",
      "system_fingerprint": None,
      "usage": None
  }
  return res  