import json
from typing import Any

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object


class CacheSerializer:

    @staticmethod
    def dumps(data: Any) -> str:
        if isinstance(data, BaseModel):
            if hasattr(data, "model_dump_json"):
                return data.model_dump_json()
            return json.dumps(data.dict(), default=str)

        if isinstance(data, list):
            result = []

            for item in data:
                if isinstance(item, BaseModel):
                    if hasattr(item, "model_dump"):
                        result.append(item.model_dump())
                    else:
                        result.append(item.dict())
                else:
                    result.append(item)

            return json.dumps(result, default=str)

        return json.dumps(data, default=str)

    @staticmethod
    def loads(data: str):
        return json.loads(data)