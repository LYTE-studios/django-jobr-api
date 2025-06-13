import requests
import jwt
import json
import base64
from jwt.algorithms import RSAAlgorithm


APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"


def get_apple_public_key_for_token(id_token: str):
    """
    Fetch the Apple public key matching the JWT's kid header and return it in PEM format.
    """
    # 1. Decode header only, do NOT verify
    headers = jwt.get_unverified_header(id_token)
    kid = headers.get("kid")
    alg = headers.get("alg", "RS256")
    if not kid:
        raise Exception("No 'kid' found in Apple ID token header.")

    # 2. Fetch Apple's jwks
    jwks = requests.get(APPLE_JWKS_URL).json()
    key = None
    for k in jwks["keys"]:
        if k["kid"] == kid and k["alg"] == alg:
            key = k
            break
    if not key:
        raise Exception("Public key not found in Apple's JWKS for kid={}".format(kid))

    # 3. Convert JWK to PEM using PyJWT internals (RSA)
    public_key = RSAAlgorithm.from_jwk(json.dumps(key))
    return public_key