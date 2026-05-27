#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <sys/mount.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <signal.h>
#include <sys/stat.h>
#include <errno.h>
#include "pati-headers/pcg.h"

int main() {
    struct dirent *entry;
    pid_t pid;
    struct dirent **namelist;
    int n = scandir("/etc/pcgconfigs", &namelist, NULL, alphasort);
    if (n < 0) {
        perror("[!]: pcgconfigs açılamadı, sistem devam edecek..");
        char *shell_args[] = {"/bin/shell", NULL};
        execv("/bin/shell", shell_args);
        while(wait(NULL) > 0);
        return 0;
    }
    printf("----------------------------------------\n");
    printf("----- MAUVYD Konfigürasyon Sistemi -----\n");
    printf("-------------Dosya Sistemi--------------\n");
    printf("-------------  Açılıyor.. --------------\n");
    mount("proc", "/proc", "proc", 0, NULL); 
    mount("sysfs", "/sys", "sysfs", 0, NULL);
    mount("devtmpfs", "/dev", "devtmpfs", 0, NULL);
    mount("tmpfs", "/tmp", "tmpfs", 0, NULL);
    mkdir("/data", 0755);
    mkdir("/data/paticommands", 0755);
    int ret = mount("/dev/vda", "/data", "ext4", 0, NULL);
    if (ret == 0) {
        printf("[+]: Kalıcı depolama aktifleştirildi.\n");
    } else if (errno == EBUSY) {
        printf("[?]: Depolama zaten bagli.\n");
    } else {
        perror("[!]: Disk baglanamadi..\n");
    }
    printf("[!] Hostname ayarlanıyor..\n");
    sethostname("patios", 6);
    putenv("PATH=/bin:/pcg-startup:/usr/bin:/data/paticommands:/lib/paticommands");
    putenv("TERM=linux");
    printf("Pati-2.1 Embedded Edition by PatiOS Team.\n");

    struct ifreq ifr;
    int tmp_fd = socket(AF_INET, SOCK_DGRAM, 0);

    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "lo", IFNAMSIZ);
    ioctl(tmp_fd, SIOCGIFFLAGS, &ifr);
    ifr.ifr_flags |= IFF_UP | IFF_RUNNING;
    ioctl(tmp_fd, SIOCSIFFLAGS, &ifr);

    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, "eth0", IFNAMSIZ);
    ioctl(tmp_fd, SIOCGIFFLAGS, &ifr);
    ifr.ifr_flags |= IFF_UP | IFF_RUNNING;
    ioctl(tmp_fd, SIOCSIFFLAGS, &ifr);

    close(tmp_fd);

for (int i = 0; i < n; i++) {
    entry = namelist[i];
    if (strcmp(entry->d_name, ".") == 0) {
        continue;
    };
    if (strcmp(entry->d_name, "..") == 0) {
        continue;
    };
      usleep(10000);
      printf("İşlem Bulundu: %s\n", entry->d_name);
      char tamyol[512];
      snprintf(tamyol, sizeof(tamyol), "/etc/pcgconfigs/%s", entry->d_name);
    char dosyayolu[256] = {0};
    char bekle_val[16] = {0};
    char izle_val[16] = {0};
    pcg_read(tamyol, "konumu", dosyayolu, sizeof(dosyayolu));
    if (dosyayolu[0] != '/' || strstr(dosyayolu, "..") != NULL) {
        printf("[!!!] Atlanıyor, geçersiz yol: %s\n", dosyayolu);
        free(namelist[i]);
        continue;
    }
    pcg_read(tamyol, "bekle", bekle_val, sizeof(bekle_val));
    pcg_read(tamyol, "izle", izle_val, sizeof(izle_val));
    char *args[] = {NULL, NULL};
    args[0] = dosyayolu;
    int bekle = (strcmp(bekle_val, "1") == 0);
    int izle = (strcmp(izle_val, "1") == 0);
        if (izle) printf("[+] %s işlemi Karabaş Tarafından izlenecektir.\n", dosyayolu);


      pid = fork(); // ÇATALLAMA ZAMANII!

    if (pid == -1) {
        perror("Çatalı Çatalladılar!1 (fork failed)");
        exit(EXIT_FAILURE);
        }
    if (pid > 0 && bekle == 1) {
        usleep(100000);
        wait(NULL);
        }

    if (pid == 0) {
        printf("Çocuk işlem şu servisi başlatıyor: %s\n", dosyayolu);
        execv(dosyayolu, args);
        perror("Oops, Pati hastalandı!");
        exit(EXIT_FAILURE);
        }
free(namelist[i]);
}
free(namelist);
signal(SIGCHLD, SIG_IGN);
while(1) pause();
}
