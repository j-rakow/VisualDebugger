#include <stdio.h>

int compute_sum(int a, int b) {
    int sum = a + b;
    return sum;
}

int compute_product(int a, int b) {
    int r;
    int product = a * b;
    //printf("%d",r);
    return product;
}

void print_result(int sum, int product) {
    printf("Sum: %d\n", sum);
    printf("Product: %d\n", product);
}

int main() {
    int x = 5;
    int y = 3;

    int m;

    printf("%d",m);

    int sum = compute_sum(x, y);
    int product = compute_product(x, y);

    print_result(sum, product);

    return 0;
}
