#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "math_utils.h"

int main() {
    printf("OpenSSL Tools Cache Test Program\n");
    printf("================================\n");
    
    // Test basic functionality
    int a = 10, b = 20;
    printf("Addition: %d + %d = %d\n", a, b, add(a, b));
    printf("Multiplication: %d * %d = %d\n", a, b, multiply(a, b));
    
    // Test with some computation to make build time measurable
    printf("\nComputing Fibonacci sequence...\n");
    for (int i = 0; i < 10; i++) {
        printf("fib(%d) = %d\n", i, fibonacci(i));
    }
    
    // Test current time
    time_t now = time(NULL);
    printf("\nBuild timestamp: %s", ctime(&now));
    
    printf("\nCache test completed successfully!\n");
    return 0;
}