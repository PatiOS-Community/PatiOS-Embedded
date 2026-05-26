#include <stdio.h>
#include <sys/stat.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("kullanım: mkdir <dizin>\n");
        return 1;
    }
    if (mkdir(argv[1], 0755) < 0) {
        perror("mkdir başarısız");
        return 1;
    }
    return 0;
    
} 
