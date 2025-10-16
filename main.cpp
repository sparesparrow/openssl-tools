#include <openssl/ssl.h>
#include <openssl/crypto.h>
#include <iostream>

int main() {
    std::cout << "OpenSSL version: " << OpenSSL_version(OPENSSL_VERSION) << std::endl;
    std::cout << "SSL library version: " << OpenSSL_version(OPENSSL_CFLAGS) << std::endl;
    return 0;
}
