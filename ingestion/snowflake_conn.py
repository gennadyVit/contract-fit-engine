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
            try:
                key_pem = key_env.replace("\\n", "\n")
                return load_pem_private_key(key_pem.encode(), password=None)
            except Exception:
                return None
    if os.path.exists("rsa_key.p8"):
        with open("rsa_key.p8", "rb") as f:
            return load_pem_private_key(f.read(), password=None)
    return None


def get_connection():
    from keyvault import get_secret
    private_key = load_private_key()
    account = get_secret("SNOWFLAKE-ACCOUNT", "SNOWFLAKE_ACCOUNT")
    user = get_secret("SNOWFLAKE-USER", "SNOWFLAKE_USER")
    warehouse = get_secret("SNOWFLAKE-WAREHOUSE", "SNOWFLAKE_WAREHOUSE")
    database = get_secret("SNOWFLAKE-DATABASE", "SNOWFLAKE_DATABASE")
    schema = get_secret("SNOWFLAKE-SCHEMA", "SNOWFLAKE_SCHEMA")

    if private_key:
        return snowflake.connector.connect(
            account=account,
            user=user,
            private_key=private_key,
            warehouse=warehouse,
            database=database,
            schema=schema,
        )
    # Fall back to password auth
    password = get_secret("SNOWFLAKE-PASSWORD", "SNOWFLAKE_PASSWORD")
    return snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        database=database,
        schema=schema,
    )
