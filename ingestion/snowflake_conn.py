import os
import base64
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key


def load_private_key():
    from keyvault import get_secret
    key_env = get_secret("SNOWFLAKE-PRIVATE-KEY", "SNOWFLAKE_PRIVATE_KEY")
    if key_env:
        try:
            der = base64.b64decode(key_env.strip())
            return serialization.load_der_private_key(der, password=None)
        except Exception:
            key_pem = key_env.replace("\\n", "\n")
            return load_pem_private_key(key_pem.encode(), password=None)
    with open("rsa_key.p8", "rb") as f:
        return load_pem_private_key(f.read(), password=None)


def get_connection():
    from keyvault import get_secret
    return snowflake.connector.connect(
        account=get_secret("SNOWFLAKE-ACCOUNT", "SNOWFLAKE_ACCOUNT"),
        user=get_secret("SNOWFLAKE-USER", "SNOWFLAKE_USER"),
        private_key=load_private_key(),
        warehouse=get_secret("SNOWFLAKE-WAREHOUSE", "SNOWFLAKE_WAREHOUSE"),
        database=get_secret("SNOWFLAKE-DATABASE", "SNOWFLAKE_DATABASE"),
        schema=get_secret("SNOWFLAKE-SCHEMA", "SNOWFLAKE_SCHEMA"),
    )
