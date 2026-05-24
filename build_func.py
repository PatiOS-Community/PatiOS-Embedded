from colorama import Fore, init
import os
import glob
import sys
import time
from Lang.lang import *

unzip_loc = "/usr/bin/unzip"
sysroot_loc = os.path.abspath("rootfs/usr")
gcc_loc = "/usr/bin/aarch64-linux-gnu-gcc"

init(autoreset=True)

def root_control():
    if os.geteuid() != 0:
        print("Please run this script as the root user.")
        sys.exit(1)

def extract():
    print(Fore.GREEN + "Dosya sistemi çıkarılıyor..")

    if not os.path.exists(unzip_loc):
        print(Fore.YELLOW + "[!] unzip bulunamadı, kuruluyor...")
        ret = os.system("sudo apt install unzip -y")
        if ret != 0:
            print(Fore.RED + "[-] unzip kurulamadı, çıkılıyor.")
            sys.exit(1)

    ret1 = os.system(f"{unzip_loc} paticommands.zip -d pati-commands/")
    ret2 = os.system(f"{unzip_loc} filesystem.zip -d rootfs/")

    if ret1 != 0 or ret2 != 0:
        print(Fore.RED + "[-] ZIP çıkartma başarısız, çıkılıyor.")
        sys.exit(1)

    print(Fore.GREEN + "[+] Dosya sistemi hazır.")


def compile():
    if not os.path.exists(gcc_loc):
        print(Fore.YELLOW + "[!] aarch64-gcc bulunamadı, kuruluyor...")
        ret = os.system("sudo apt install gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu -y")
        if ret != 0:
            print(Fore.RED + "[-] GCC kurulamadı, çıkılıyor.")
            sys.exit(1)

    dosyalar = glob.glob("pati-commands/*.c")
    if not dosyalar:
        print(Fore.RED + "[-] pati-commands/ içinde .c dosyası bulunamadı.")
        sys.exit(1)

    sysroot = os.path.abspath("rootfs/usr")
    flags = f"--sysroot={sysroot} -I{sysroot}/include -I/usr/include -L{sysroot}/lib -static"

    basari = 0
    hata = 0
    for f in dosyalar:
        out = f.replace(".c", "")
        if "mauvyd.c" in f:
            ret = os.system(f"{gcc_loc} {flags} -Ipati-commands/pati-headers {f} pati-commands/pati-headers/pcg.c -o {out}")
        elif "psp.c" in f:
            user = input("Kullanıcı adını gir >> ")
            libcrypto_path = f"/home/{user}/KedyBox/libcrypto.a"
            ret = os.system(f"{gcc_loc} {flags} {f} {libcrypto_path} -o {out}")
        else:
            ret = os.system(f"{gcc_loc} {flags} {f} -o {out}")
        if ret == 0:
            print(Fore.GREEN + f"[+] Derlendi: {f} -> {out}")
            basari += 1
        else:
            print(Fore.RED + f"[-] Hata: {f}")
            hata += 1
    print(Fore.GREEN + f"[+] Derleme tamam: {basari} başarılı, {hata} hatalı.")


def create_nodes():
    print(Fore.GREEN + "[+] Device nodes oluşturuluyor...")
    os.system("sudo rm -f rootfs/dev/vda rootfs/dev/fb0 rootfs/dev/rtc0 rootfs/dev/urandom")
    os.system("sudo mknod rootfs/dev/vda b 254 0")
    os.system("sudo mknod rootfs/dev/fb0 c 29 0")
    os.system("sudo mknod rootfs/dev/rtc0 c 253 0")
    os.system("sudo mknod rootfs/dev/urandom c 1 9")

def move():
    os.makedirs("rootfs/lib/paticommands", exist_ok=True)

    if os.path.exists("pati-commands/mauvyd"):
        os.system("cp pati-commands/mauvyd rootfs/init")
        os.system("rm -f pati-commands/mauvyd")
    if os.path.exists("pati-commands/shell"):
        os.system("cp pati-commands/shell rootfs/bin/")
        os.system("rm -f pati-commands/shell")

    for f in glob.glob("pati-commands/*"):
        if not f.endswith(".c") and os.path.isfile(f):
            os.system(f"cp {f} rootfs/lib/paticommands/")
            print(Fore.GREEN + f"[+] Taşındı: {f}")
            os.system(f"rm -f {f}")
    os.system("rm -f rootfs/lib/paticommands/init rootfs/lib/paticommands/shell")
    print(Fore.GREEN + "[+] initramfs oluşturuluyor...")
    ret = os.system("cd rootfs && find . | cpio -o -H newc | gzip -9 > ../initramfs.cpio.gz")
    if ret == 0:
        print(Fore.GREEN + "[+] initramfs.cpio.gz hazır.")
    else:
        print(Fore.RED + "[-] initramfs oluşturulamadı.")
        sys.exit(1)


extract()
compile()
create_nodes()
move()
