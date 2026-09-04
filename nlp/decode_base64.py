import base64
import html
import re
import binascii

def decode_base64(value):
    """Decodes base64 string"""
    try:
        raw = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError):
        return None

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None

    # Decode HTML
    text = html.unescape(text)

    # If HTML is present convert tags to new lines
    if re.search(r"<[a-zA-Z][^>]*>", text):
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
        text = re.sub(r"</p\s*>", "\n\n", text, flags=re.I)
        text = re.sub(r"</div\s*>", "\n", text, flags=re.I)

        # Remove remaining HTML tags
        text = re.sub(r"<[^>]+>", "", text)

    # Normalize spaces and tabs, preserve new lines
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def find_base64(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "data" and isinstance(value, str):
                decoded = decode_base64(value)
                if decoded is not None:
                    yield decoded
            yield from find_base64(value)

    elif isinstance(obj, list):
        for value in obj:
            yield from find_base64(value)