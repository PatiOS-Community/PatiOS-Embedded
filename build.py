import platform, build_func
from colorama import Fore

if platform.system() == "Linux":
    print(Fore.RED + "KedyBox - PatiOS ENV Builder by mehmetdemir-tr")
    
    build_func.root_control()
    build_func.extract()
    build_func.compile()
    build_func.create_nodes()
    build_func.move()
else:
    print("You cannot run this script on your system. Please make sure you are using a Linux-based (like Ubuntu or WSL) operating system")
