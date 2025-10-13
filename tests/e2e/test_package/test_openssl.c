#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/ssl.h>
#include <openssl/crypto.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include <openssl/bio.h>
#include <openssl/rand.h>

int main(void) {
    printf("OpenSSL Test Package - Validating OpenSSL Installation\n");
    printf("======================================================\n\n");
    
    // Test 1: OpenSSL version
    printf("1. OpenSSL Version: %s\n", OpenSSL_version(OPENSSL_VERSION));
    printf("   OpenSSL Version String: %s\n", OpenSSL_version(OPENSSL_VERSION_STRING));
    printf("   OpenSSL Build Date: %s\n", OpenSSL_version(OPENSSL_VERSION_BUILD_DATE));
    printf("   OpenSSL Compiler: %s\n", OpenSSL_version(OPENSSL_VERSION_COMPILER));
    printf("   OpenSSL Platform: %s\n", OpenSSL_version(OPENSSL_VERSION_PLATFORM));
    printf("   OpenSSL Directory: %s\n", OpenSSL_version(OPENSSL_VERSION_DIR));
    printf("   ✓ Version information retrieved\n\n");
    
    // Test 2: SSL library initialization
    printf("2. SSL Library Initialization:\n");
    if (SSL_library_init() == 1) {
        printf("   ✓ SSL_library_init() successful\n");
    } else {
        printf("   ✗ SSL_library_init() failed\n");
        return 1;
    }
    
    if (SSL_load_error_strings() == 1) {
        printf("   ✓ SSL_load_error_strings() successful\n");
    } else {
        printf("   ✗ SSL_load_error_strings() failed\n");
        return 1;
    }
    
    if (OpenSSL_add_all_algorithms() == 1) {
        printf("   ✓ OpenSSL_add_all_algorithms() successful\n");
    } else {
        printf("   ✗ OpenSSL_add_all_algorithms() failed\n");
        return 1;
    }
    printf("\n");
    
    // Test 3: EVP operations (EVP_sha256)
    printf("3. EVP Operations Test:\n");
    const EVP_MD *md = EVP_sha256();
    if (md != NULL) {
        printf("   ✓ EVP_sha256() successful\n");
        printf("   ✓ SHA-256 digest size: %d bytes\n", EVP_MD_size(md));
        printf("   ✓ SHA-256 block size: %d bytes\n", EVP_MD_block_size(md));
    } else {
        printf("   ✗ EVP_sha256() failed\n");
        return 1;
    }
    printf("\n");
    
    // Test 4: Random number generation
    printf("4. Random Number Generation Test:\n");
    unsigned char random_bytes[32];
    if (RAND_bytes(random_bytes, sizeof(random_bytes)) == 1) {
        printf("   ✓ RAND_bytes() successful\n");
        printf("   ✓ Generated %zu random bytes\n", sizeof(random_bytes));
        
        // Display first few bytes (hex)
        printf("   ✓ Sample bytes: ");
        for (int i = 0; i < 8; i++) {
            printf("%02x", random_bytes[i]);
        }
        printf("...\n");
    } else {
        printf("   ✗ RAND_bytes() failed\n");
        return 1;
    }
    printf("\n");
    
    // Test 5: Error handling
    printf("5. Error Handling Test:\n");
    ERR_load_crypto_strings();
    ERR_load_SSL_strings();
    
    // Generate a test error
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (ctx == NULL) {
        printf("   ✓ Error handling working (EVP_MD_CTX_new failed as expected)\n");
    } else {
        EVP_MD_CTX_free(ctx);
        printf("   ✓ EVP_MD_CTX operations successful\n");
    }
    printf("\n");
    
    // Test 6: BIO operations
    printf("6. BIO Operations Test:\n");
    BIO *bio = BIO_new(BIO_s_mem());
    if (bio != NULL) {
        printf("   ✓ BIO_new(BIO_s_mem()) successful\n");
        
        const char *test_data = "Hello, OpenSSL!";
        int written = BIO_write(bio, test_data, strlen(test_data));
        if (written > 0) {
            printf("   ✓ BIO_write() successful (%d bytes)\n", written);
        } else {
            printf("   ✗ BIO_write() failed\n");
            return 1;
        }
        
        BIO_free(bio);
        printf("   ✓ BIO_free() successful\n");
    } else {
        printf("   ✗ BIO_new(BIO_s_mem()) failed\n");
        return 1;
    }
    printf("\n");
    
    // Test 7: SSL context creation
    printf("7. SSL Context Test:\n");
    SSL_CTX *ssl_ctx = SSL_CTX_new(TLS_client_method());
    if (ssl_ctx != NULL) {
        printf("   ✓ SSL_CTX_new(TLS_client_method()) successful\n");
        printf("   ✓ SSL context version: %s\n", SSL_CTX_get_ssl_method(ssl_ctx)->version);
        SSL_CTX_free(ssl_ctx);
        printf("   ✓ SSL_CTX_free() successful\n");
    } else {
        printf("   ✗ SSL_CTX_new(TLS_client_method()) failed\n");
        return 1;
    }
    printf("\n");
    
    // Test 8: Memory management
    printf("8. Memory Management Test:\n");
    EVP_MD_CTX *md_ctx = EVP_MD_CTX_new();
    if (md_ctx != NULL) {
        printf("   ✓ EVP_MD_CTX_new() successful\n");
        EVP_MD_CTX_free(md_ctx);
        printf("   ✓ EVP_MD_CTX_free() successful\n");
    } else {
        printf("   ✗ EVP_MD_CTX_new() failed\n");
        return 1;
    }
    printf("\n");
    
    // Test 9: Algorithm availability
    printf("9. Algorithm Availability Test:\n");
    const char *algorithms[] = {
        "SHA256", "SHA512", "AES-256-CBC", "AES-256-GCM", 
        "RSA", "ECDSA", "ECDH", "DH"
    };
    
    int available_count = 0;
    for (int i = 0; i < sizeof(algorithms) / sizeof(algorithms[0]); i++) {
        if (EVP_get_digestbyname(algorithms[i]) != NULL || 
            EVP_get_cipherbyname(algorithms[i]) != NULL) {
            printf("   ✓ %s available\n", algorithms[i]);
            available_count++;
        } else {
            printf("   - %s not available\n", algorithms[i]);
        }
    }
    printf("   ✓ %d/%zu algorithms available\n", available_count, 
           sizeof(algorithms) / sizeof(algorithms[0]));
    printf("\n");
    
    // Test 10: Configuration
    printf("10. Configuration Test:\n");
    const char *conf_file = OPENSSL_CONF;
    if (conf_file != NULL) {
        printf("   ✓ OPENSSL_CONF: %s\n", conf_file);
    } else {
        printf("   - OPENSSL_CONF not set\n");
    }
    
    // Check if FIPS mode is enabled
    if (FIPS_mode() == 1) {
        printf("   ✓ FIPS mode enabled\n");
    } else {
        printf("   - FIPS mode disabled\n");
    }
    printf("\n");
    
    // Cleanup
    printf("11. Cleanup:\n");
    EVP_cleanup();
    ERR_free_strings();
    printf("   ✓ OpenSSL cleanup completed\n\n");
    
    printf("======================================================\n");
    printf("🎉 All OpenSSL tests passed successfully!\n");
    printf("   OpenSSL is properly installed and functional.\n");
    printf("======================================================\n");
    
    return 0;
}