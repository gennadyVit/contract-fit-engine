"""
Loads secrets from Azure Key Vault when running in Azure (managed identity),
falls back to environment variables for local development.
"""
import os

_kv_client = None
_kv_enabled = False


def _init_kv():
    global _kv_client, _kv_enabled
    vault_url = os.getenv("AZURE_KEYVAULT_URL", "https://govcontract-kv.vault.azure.net/")
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
        credential = DefaultAzureCredential()
        _kv_client = SecretClient(vault_url=vault_url, credential=credential)
        # Test connectivity
        _kv_client.get_secret("SNOWFLAKE-ACCOUNT")
        _kv_enabled = True
        print("Key Vault: connected")
    except Exception as e:
        _kv_enabled = False
        print(f"Key Vault: falling back to env vars ({e})")


def get_secret(name: str, env_var: str = None) -> str:
    """
    Get a secret by Key Vault name (e.g. 'SNOWFLAKE-ACCOUNT').
    Falls back to env_var (or name with dashes→underscores) if KV unavailable.
    """
    global _kv_client, _kv_enabled
    if _kv_client is None:
        _init_kv()

    if _kv_enabled:
        try:
            return _kv_client.get_secret(name).value
        except Exception:
            pass

    # Fall back to env var
    fallback = env_var or name.replace("-", "_")
    return os.getenv(fallback, "")
