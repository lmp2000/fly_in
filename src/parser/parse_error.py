class ParseError(Exception):
    """Raised when a map or metadata line violates the expected format."""

    def __init__(self, line_number: int, message: str) -> None:
        """Create a parse error with source line context.

        Args:
            line_number: One-based line number where the error occurred.
            message: Human-readable error description.
        """
        self.line_number = line_number
        self.message = message
        super().__init__(f"Line {line_number}: {message}")
