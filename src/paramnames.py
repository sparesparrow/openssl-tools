#!/usr/bin/env python3
"""
OpenSSL Parameter Names - Python replacement for paramnames.pm

Handles parameter name mappings and macro generation for OpenSSL providers.
"""

import re
from typing import Dict, List, Tuple, Optional


class ParamNames:
    """OpenSSL parameter names and macros handler."""

    def __init__(self):
        self.case_sensitive = True
        self.need_break = False
        self.invalid_param = "invalid param"

        # Well known parameter names mapping
        self.params: Dict[str, str] = {
            # Well known parameter names that core passes to providers
            'OSSL_PROV_PARAM_CORE_VERSION': "openssl-version",  # utf8_ptr
            'OSSL_PROV_PARAM_CORE_PROV_NAME': "provider-name",  # utf8_ptr
            'OSSL_PROV_PARAM_CORE_MODULE_FILENAME': "module-filename",  # utf8_ptr

            # Well known parameter names that Providers can define
            'OSSL_PROV_PARAM_NAME': "name",  # utf8_ptr
            'OSSL_PROV_PARAM_VERSION': "version",  # utf8_ptr
            'OSSL_PROV_PARAM_BUILDINFO': "buildinfo",  # utf8_ptr
            'OSSL_PROV_PARAM_STATUS': "status",  # uint
            'OSSL_PROV_PARAM_SECURITY_CHECKS': "security-checks",  # uint
            'OSSL_PROV_PARAM_HMAC_KEY_CHECK': "hmac-key-check",  # uint
            'OSSL_PROV_PARAM_KMAC_KEY_CHECK': "kmac-key-check",  # uint
            'OSSL_PROV_PARAM_TLS1_PRF_EMS_CHECK': "tls1-prf-ems-check",  # uint
            'OSSL_PROV_PARAM_NO_SHORT_MAC': "no-short-mac",  # uint
            'OSSL_PROV_PARAM_DRBG_TRUNC_DIGEST': "drbg-no-trunc-md",  # uint
            'OSSL_PROV_PARAM_HKDF_DIGEST_CHECK': "hkdf-digest-check",  # uint
            'OSSL_PROV_PARAM_TLS13_KDF_DIGEST_CHECK': "tls13-kdf-digest-check",  # uint
            'OSSL_PROV_PARAM_TLS1_PRF_DIGEST_CHECK': "tls1-prf-digest-check",  # uint
            'OSSL_PROV_PARAM_SSHKDF_DIGEST_CHECK': "sshkdf-digest-check",  # uint
            'OSSL_PROV_PARAM_SSKDF_DIGEST_CHECK': "sskdf-digest-check",  # uint
            'OSSL_PROV_PARAM_X963KDF_DIGEST_CHECK': "x963kdf-digest-check",  # uint
            'OSSL_PROV_PARAM_DSA_SIGN_DISABLED': "dsa-sign-disabled",  # uint
            'OSSL_PROV_PARAM_TDES_ENCRYPT_DISABLED': "tdes-encrypt-disabled",  # uint
            'OSSL_PROV_PARAM_RSA_PSS_SALTLEN_CHECK': "rsa-pss-saltlen-check",  # uint
            'OSSL_PROV_PARAM_RSA_SIGN_X931_PAD_DISABLED': "rsa-sign-x931-pad-disabled",  # uint
            'OSSL_PROV_PARAM_RSA_PKCS15_PAD_DISABLED': "rsa-pkcs15-pad-disabled",  # uint
            'OSSL_PROV_PARAM_HKDF_KEY_CHECK': "hkdf-key-check",  # uint
            'OSSL_PROV_PARAM_KBKDF_KEY_CHECK': "kbkdf-key-check",  # uint
            'OSSL_PROV_PARAM_TLS13_KDF_KEY_CHECK': "tls13-kdf-key-check",  # uint
            'OSSL_PROV_PARAM_TLS1_PRF_KEY_CHECK': "tls1-prf-key-check",  # uint
            'OSSL_PROV_PARAM_SSHKDF_KEY_CHECK': "sshkdf-key-check",  # uint
            'OSSL_PROV_PARAM_SSKDF_KEY_CHECK': "sskdf-key-check",  # uint
            'OSSL_PROV_PARAM_X963KDF_KEY_CHECK': "x963kdf-key-check",  # uint
            'OSSL_PROV_PARAM_X942KDF_KEY_CHECK': "x942kdf-key-check",  # uint
            'OSSL_PROV_PARAM_PBKDF2_LOWER_BOUND_CHECK': "pbkdf2-lower-bound-check",  # uint
            'OSSL_PROV_PARAM_ECDH_COFACTOR_CHECK': "ecdh-cofactor-check",  # uint
            'OSSL_PROV_PARAM_SIGNATURE_DIGEST_CHECK': "signature-digest-check",  # uint

            # Self test callback parameters
            'OSSL_PROV_PARAM_SELF_TEST_PHASE': "st-phase",  # utf8_string
            'OSSL_PROV_PARAM_SELF_TEST_TYPE': "st-type",  # utf8_string
            'OSSL_PROV_PARAM_SELF_TEST_DESC': "st-desc",  # utf8_string

            # Provider-native object abstractions
            'OSSL_OBJECT_PARAM_TYPE': "type",  # INTEGER
            'OSSL_OBJECT_PARAM_DATA_TYPE': "data-type",  # UTF8_STRING
            'OSSL_OBJECT_PARAM_DATA_STRUCTURE': "data-structure",  # UTF8_STRING
            'OSSL_OBJECT_PARAM_REFERENCE': "reference",  # OCTET_STRING
            'OSSL_OBJECT_PARAM_DATA': "data",  # OCTET_STRING or UTF8_STRING
            'OSSL_OBJECT_PARAM_DESC': "desc",  # UTF8_STRING
            'OSSL_OBJECT_PARAM_INPUT_TYPE': "input-type",  # UTF8_STRING

            # Algorithm parameters
            'OSSL_ALG_PARAM_DIGEST': "digest",  # utf8_string
            'OSSL_ALG_PARAM_CIPHER': "cipher",  # utf8_string
            'OSSL_ALG_PARAM_ENGINE': "engine",  # utf8_string
            'OSSL_ALG_PARAM_MAC': "mac",  # utf8_string
            'OSSL_ALG_PARAM_PROPERTIES': "properties",  # utf8_string
            'OSSL_ALG_PARAM_FIPS_APPROVED_INDICATOR': 'fips-indicator',  # int, -1, 0 or 1
            'OSSL_ALG_PARAM_SECURITY_CATEGORY': "security-category",  # int, 0 .. 5
        }

        # Continue with more parameter mappings...
        self._load_extended_params()

    def _load_extended_params(self) -> None:
        """Load extended parameter mappings."""
        # Add more parameter mappings as needed
        extended_params = {
            # MAC parameters
            'OSSL_MAC_PARAM_DIGEST': "digest",  # utf8_string
            'OSSL_MAC_PARAM_PROPERTIES': "properties",  # utf8_string
            'OSSL_MAC_PARAM_SIZE': "size",  # size_t
            'OSSL_MAC_PARAM_BLOCK_SIZE': "block-size",  # size_t
            'OSSL_MAC_PARAM_KEY': "key",  # octet_string
            'OSSL_MAC_PARAM_IV': "iv",  # octet_string
            'OSSL_MAC_PARAM_CUSTOM': "custom",  # octet_string
            'OSSL_MAC_PARAM_SALT': "salt",  # octet_string
            'OSSL_MAC_PARAM_XOF': "xof",  # int
            'OSSL_MAC_PARAM_TLS_DATA': "tls-data",  # octet_string

            # KDF parameters
            'OSSL_KDF_PARAM_PROPERTIES': "properties",  # utf8_string
            'OSSL_KDF_PARAM_DIGEST': "digest",  # utf8_string
            'OSSL_KDF_PARAM_CIPHER': "cipher",  # utf8_string
            'OSSL_KDF_PARAM_MAC': "mac",  # utf8_string
            'OSSL_KDF_PARAM_PASSWORD': "password",  # octet_string
            'OSSL_KDF_PARAM_SALT': "salt",  # octet_string
            'OSSL_KDF_PARAM_SEED': "seed",  # octet_string
            'OSSL_KDF_PARAM_INFO': "info",  # octet_string
            'OSSL_KDF_PARAM_LABEL': "label",  # octet_string
            'OSSL_KDF_PARAM_KEY': "key",  # octet_string
            'OSSL_KDF_PARAM_DATA': "data",  # octet_string
            'OSSL_KDF_PARAM_CONSTANT': "constant",  # octet_string
            'OSSL_KDF_PARAM_PKCS5': "pkcs5",  # int
            'OSSL_KDF_PARAM_UKM': "ukm",  # octet_string
            'OSSL_KDF_PARAM_CEK_ALG': "cek-alg",  # utf8_string
            'OSSL_KDF_PARAM_MODE': "mode",  # utf8_string
            'OSSL_KDF_PARAM_ITER': "iter",  # unsigned int
            'OSSL_KDF_PARAM_SIZE': "size",  # size_t
            'OSSL_KDF_PARAM_THREADS': "threads",  # unsigned int
            'OSSL_KDF_PARAM_EARLY_CLEAN': "early-clean",  # int
            'OSSL_KDF_PARAM_MAXMEM_BYTES': "maxmem-bytes",  # uint64_t
            'OSSL_KDF_PARAM_SSHKDF_TYPE': "sshkdf-type",  # utf8_string
            'OSSL_KDF_PARAM_SSHKDF_SESSION_ID': "sshkdf-session-id",  # octet_string
            'OSSL_KDF_PARAM_SSHKDF_XCGHASH': "sshkdf-xcghash",  # utf8_string
        }

        self.params.update(extended_params)

    def generate_public_macros(self, output_file: str) -> None:
        """Generate public macro definitions."""
        with open(output_file, 'w') as f:
            f.write("/*\n")
            f.write(" * Generated parameter name macros\n")
            f.write(" * Do not edit manually - generated by paramnames.py\n")
            f.write(" */\n\n")

            for param, value in sorted(self.params.items()):
                f.write(f"#define {param} \"{value}\"\n")

    def produce_param_decoder(self, param_name: str) -> Optional[str]:
        """Produce parameter decoder for given parameter name."""
        if param_name in self.params:
            return self.params[param_name]

        # Handle special cases or patterns
        if param_name.startswith('OSSL_') and param_name.endswith('_PARAM_'):
            # Try to extract the base name
            base = param_name.replace('OSSL_', '').replace('_PARAM_', '').lower()
            base = base.replace('_', '-')
            return base

        return None

    def get_all_params(self) -> Dict[str, str]:
        """Get all parameter mappings."""
        return self.params.copy()

    def lookup_param(self, key: str) -> Optional[str]:
        """Lookup a parameter value by key."""
        return self.params.get(key)


# Export functions for compatibility
def generate_public_macros(output_file: str) -> None:
    """Generate public macro definitions."""
    handler = ParamNames()
    handler.generate_public_macros(output_file)


def produce_param_decoder(param_name: str) -> Optional[str]:
    """Produce parameter decoder for given parameter name."""
    handler = ParamNames()
    return handler.produce_param_decoder(param_name)


if __name__ == '__main__':
    # Simple test/demo
    handler = ParamNames()
    print(f"Total parameters: {len(handler.params)}")

    # Test some lookups
    test_params = [
        'OSSL_PROV_PARAM_NAME',
        'OSSL_MAC_PARAM_DIGEST',
        'OSSL_KDF_PARAM_PASSWORD'
    ]

    for param in test_params:
        value = handler.lookup_param(param)
        print(f"{param} -> {value}")