class LLMMalformedActionError(Exception):
    def __init__(self, message: str = "Malformed response") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message
