"""Reference bit-string framing. No byte alignment or cryptographic claim."""
NULL = "00000000"

def valid(bits: str) -> bool:
    return bool(bits) and set(bits) <= {"0", "1"} and bits[0] == bits[-1] == "1" and NULL not in bits

def notion_ids(count: int) -> list[str]:
    """Provisional enumeration in ascending integer order, starting at 1."""
    if count < 0:
        raise ValueError("negative count")
    result, value = [], 1
    while len(result) < count:
        bits = format(value, "b")
        if valid(bits):
            result.append(bits)
        value += 2
    return result

def encode(ids: list[str]) -> str:
    if not all(valid(i) for i in ids):
        raise ValueError("invalid notion identifier")
    return NULL.join(ids)

def decode(stream: str) -> list[str]:
    if not stream:
        return []
    ids = stream.split(NULL)
    if not all(valid(i) for i in ids):
        raise ValueError("malformed stream or empty notion")
    return ids
