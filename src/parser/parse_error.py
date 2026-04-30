class ParseError(Exception):
    def __init__(self, line_number: int, message: str) -> None:
        self.line_number = line_number
        self.message = message
        super().__init__(f"Line {line_number}: {message}")
