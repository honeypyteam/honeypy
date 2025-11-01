import uuid

from src.honeypy import HoneyPy


class MinimalPlugin(HoneyPy):
    def __init__(self):
        super().__init__()

    def package_id(self) -> uuid.UUID:
        return uuid.UUID("124b012e-c249-4874-a1ab-7705cefe0fe5")

    def package_name(self) -> str:
        return "Minimal Research Tool"

    def cli_name(self) -> str:
        return "minimal-research-tool"
