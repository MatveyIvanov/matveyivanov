import hashlib
import hmac


def hash_github_payload_and_compare(
    value: bytes | str,
    expected: str,
    key: str = "token",
) -> bool:
    hashed = hmac.new(
        key.encode("utf-8"),
        msg=value if isinstance(value, bytes) else value.encode(),
        digestmod=hashlib.sha256,
    )
    signature = "sha256=" + hashed.hexdigest()
    return hmac.compare_digest(signature, expected)
