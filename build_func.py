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
    print(Fore.GREEN + fs_unzip_content)

    if not os.path.exists(unzip_loc):
        print(Fore.YELLOW + unzip_not_found_error)
        ret = os.system("sudo apt install unzip -y")
        if ret != 0:
            print(Fore.RED + unzip_not_setup_error)
            sys.exit(1)

    ret1 = os.system(f"{unzip_loc} paticommands.zip -d pati-commands/")
    ret2 = os.system(f"{unzip_loc} filesystem.zip -d rootfs/")

    if ret1 != 0 or ret2 != 0:
        print(Fore.RED + unzip_not_success_error)
        sys.exit(1)

    print(Fore.GREEN + fs_success)

def compile():
    if not os.path.exists(gcc_loc):
        print(Fore.YELLOW + aarch64_gcc_not_found_error)
        ret = os.system("sudo apt install gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu -y")
        if ret != 0:
            print(Fore.RED + gcc_not_setup_error)
            sys.exit(1)

    dosyalar = glob.glob("pati-commands/*.c")
    if not dosyalar:
        print(Fore.RED + pati_commands_file_not_found_error)
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
        else:
            ret = os.system(f"{gcc_loc} {flags} {f} -o {out}")
        if ret == 0:
            print(Fore.GREEN + f"{compile_success} {f} -> {out}")
            basari += 1
        else:
            print(Fore.RED + f"{compile_not_success} {f}")
            hata += 1
    print(Fore.GREEN + f"{compilation_complete} {basari} {success}, {hata} {incorrect}")

def create_nodes():
        print(Fore.GREEN + create_dev_nodes)
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
            print(Fore.GREEN + f"{moved} {f}")
            os.system(f"rm -f {f}")
    os.system("rm -f rootfs/lib/paticommands/init rootfs/lib/paticommands/shell")
    print(Fore.GREEN + create_initramfs)
    ret = os.system("cd rootfs && find . | cpio -o -H newc | gzip -9 > ../initramfs.cpio.gz")
    if ret == 0:
        print(Fore.GREEN + initramfs_ready)
    else:
        print(Fore.RED + not_create_initramfs)
        sys.exit(1)
