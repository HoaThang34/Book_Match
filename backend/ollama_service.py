import json
import re

import requests
from flask import current_app


class OllamaError(Exception):
    pass


def chat_completion(system: str, user: str) -> str:
    base = current_app.config["OLLAMA_BASE_URL"]
    model = current_app.config["OLLAMA_MODEL"]
    timeout = current_app.config["OLLAMA_TIMEOUT"]

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {
            "temperature": current_app.config["OLLAMA_TEMPERATURE"],
            "top_p": current_app.config["OLLAMA_TOP_P"],
            "num_predict": current_app.config["OLLAMA_NUM_PREDICT"],
        },
    }

    try:
        response = requests.post(
            f"{base}/api/chat",
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise OllamaError("Không kết nối được Ollama. Kiểm tra OLLAMA_BASE_URL và dịch vụ Ollama.") from exc

    if response.status_code != 200:
        error_msg = ""
        try:
            error_msg = response.json().get("error", "")
        except ValueError:
            error_msg = response.text
            
        if error_msg:
            raise OllamaError(f"Ollama trả lỗi HTTP {response.status_code}: {error_msg}")
        raise OllamaError(f"Ollama trả lỗi HTTP {response.status_code}.")

    data = response.json()
    content = (data.get("message") or {}).get("content", "").strip()
    if not content:
        raise OllamaError("Ollama không trả nội dung.")
    return content


def extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise OllamaError("Không phân tích được JSON từ phản hồi AI.")
