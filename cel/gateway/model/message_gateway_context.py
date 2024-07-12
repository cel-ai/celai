from abc import ABC
from dataclasses import dataclass
from fastapi import APIRouter


@dataclass
class MessageGatewayContext(ABC):
    router: APIRouter
    webhook_url: str
    