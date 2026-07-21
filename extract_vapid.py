import sys, os
sys.path.insert(0, '/home/madfella/peptidetrack')

# The PEM private key
pem_key = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgLg17/ylCBG3YbQxm
9fW/J1CpqrhBO6kW3C4ZOcRMJGuhRANCAASV8/Oug9d1s1rMtVXFudHIoHaNvKNK
ASkQ9URzpLvXYTZP5LhcF3Qn5oqnOTf9nihPJh10/jxvHRAHaWotQzEO
-----END PRIVATE KEY-----"""

# Extract the raw EC private key bytes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ec import SECP256R1
import base64

key = load_pem_private_key(pem_key.encode(), password=None)
private_bytes = key.private_numbers().private_value.to_bytes(32, 'big')
raw_b64 = base64.urlsafe_b64encode(private_bytes).rstrip(b'=').decode()
print('Raw base64url private key:')
print(raw_b64)
print(f'\nLength: {len(raw_b64)}')
