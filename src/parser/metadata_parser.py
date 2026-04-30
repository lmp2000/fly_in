from src.parser.parse_error import ParseError


def parse_metadata(raw_metadata: str, line_number: int) -> dict[str, str]:
    text = raw_metadata.strip()
    if not text or text[0] != '[' or text[-1] != ']':
        raise ParseError(line_number, 'invalid metadata syntax')
    clean_text = text[1:-1].strip()
    fields = clean_text.split()
    result: dict[str, str] = {}
    for field in fields:
        args = field.split('=', 1)
        if len(args) != 2:
            raise ParseError(line_number, 'invalid metadata syntax')
        result[args[0]] = args[1]
    return result