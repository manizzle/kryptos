#include <stdio.h>
#include <stdlib.h>

double func1(int x) {
    return 1.00 * (x * 5);
}

double func2(int y, double f) {
    return f * f - y;
}

int main(void) {
    int x = 5;
    double t;
    t = func1(x);
    t = func2(x, t);
    printf("hello\n");
    return 0;
}


   
  
