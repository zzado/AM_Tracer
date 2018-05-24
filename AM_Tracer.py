#-*- coding: utf-8 -*-
import time
import sys, os
import colorama
import subprocess
import progressbar
colorama.init(autoreset=True, convert=True)

"""
### VAR for DEV & DEBUG

_APK_PATH = "C:\\Users\\USER\\Desktop\\AM_Tracer\\origin_app-ncs-release-v2.3.1.apk"
_SOURCE_PATH = "C:\\Users\\USER\\Desktop\\AM_Tracer\\unpak_origin_app-ncs-release-v2.3.1"
_APK_NAME = os.path.basename(_APK_PATH) 
_APKTOOLS = "apktool_2.3.3.jar"
_SMALI_AM_TRACER = ""

"""

# TEST KEY &  VAR

_PEM = "signapk\\certificate.pem"
_PK8 = "signapk\\key.pk8"
APKTOOLS = "apktool_2.3.3.jar"
SIGNAPK = "signapk\\signapk.jar"
DATA_AM_TRACER = ""

def banner():
    title = """
      ___  ___  ___  _____                       
     / _ \ |  \/  | |_   _|                      
    / /_\ \| .  . |   | |_ __ __ _  ___ ___ _ __ 
    |  _  || |\/| |   | | '__/ _` |/ __/ _ \ '__|
    | | | || |  | |   | | | | (_| | (_|  __/ |   
    \_| |_/\_|  |_/   \_/_|  \__,_|\___\___|_|
    """
    print colorama.Style.BRIGHT + colorama.Fore.GREEN + title
    print "\t0) Unpack APK"
    print "\t1) Rebuild APK"
    print "\t2) Inject AM Tracer to smali"
    print "\t3) Exit"
    print "\n"

# log function // 0 : success meassage, 1 : error message, 2 : info message, 3: input message
def log(TEXT, TYPE) :
    if TYPE is 0 :
        return "[" + colorama.Fore.GREEN + "*" + colorama.Fore.WHITE + "] "+ TEXT
    elif TYPE is 1 :
        return "[" + colorama.Fore.RED + "!" + colorama.Fore.WHITE + "] "+ TEXT
    elif TYPE is 2:
        return "[" + colorama.Fore.BLUE + "+" + colorama.Fore.WHITE + "] "+ TEXT
    elif TYPE is 3:
        return colorama.Fore.BLACK + colorama.Back.WHITE + colorama.Style.DIM + TEXT


def loading_bar(TIME) : 
    sys.stdout.flush()
    sys.stdout.write("[" + colorama.Fore.YELLOW + "-" + colorama.Fore.WHITE + "] ")
    TEXT = "LOADING....."
    
    for char in TEXT :
        sys.stdout.write(char)
        time.sleep(TIME)
        
    for char in TEXT :
        sys.stdout.write("\b")
        sys.stdout.flush()
        time.sleep(TIME)
    
    sys.stdout.write("\r")
    sys.stdout.flush()
    
    

def unpack() :
    _APK_PATH = raw_input(log("Input APK's PATH >> ",3))

    if not os.path.exists(_APK_PATH) :
        print log("APK doesn't exist! - ", 1)
        return

    _APK_NAME = os.path.basename(_APK_PATH)

    if os.path.splitext(_APK_NAME)[1] != ".apk" :
        print log("This file isn't APK! - ", 1)
        return
    
    _RESULT_PATH = "%s\\Unpaked_%s" % (os.getcwd(), _APK_NAME)

    _COMMAND = "java -jar ./%s decode %s -o %s -f" % (APKTOOLS, _APK_PATH, _RESULT_PATH[:-4])
    
    F_NULL = open(os.devnull, "w")
    proc = subprocess.Popen(_COMMAND, shell=True, stdout = F_NULL, stderr = subprocess.PIPE)

    while proc.poll() is None :
        loading_bar(0.1)
    
    F_NULL.close()

    if proc.returncode is 0 :
        print log("Unpack sucesss!", 0)
        print log(_RESULT_PATH[:-4], 2)
    else :
        print log("Unpack failed!", 1)
        


def rebuild() :
    _DIR_PATH = raw_input(log("Input Source directory PATH >> ",3))

    if not os.path.exists(_DIR_PATH) :
        print log("Direcotry doesn't exist! - " , 1)
        return

    if not os.path.isdir(_DIR_PATH) :
        print log("Your input path isn't directory! - ", 1)
        return

    _RESULT_PATH = "%s\\Rebuiled_%s.apk" %(os.getcwd(), os.path.basename(_DIR_PATH))

    _COMMAND = "java -jar ./%s build %s -o %s" % (APKTOOLS, _DIR_PATH, _RESULT_PATH)

    F_NULL = open(os.devnull, "w")
    proc = subprocess.Popen(_COMMAND, shell=True, stdout = F_NULL, stderr = subprocess.PIPE)

    while proc.poll() is None :
        loading_bar(0.1)
    
    F_NULL.close()
    
    if proc.returncode is 0 :
        print log("Rebuild sucesss!", 0)
        print log(_RESULT_PATH, 2)
        print log("Signing rebuilded APK.. !", 0)
        sign(_RESULT_PATH)
    else :
        print log("Rebuild failed!", 1)
    

def sign(_PATH) :
    _RESULT_PATH = "%s\\Signed_%s" % (os.getcwd(), os.path.basename(_PATH))
    _COMMAND = "java -jar  ./%s ./%s ./%s %s %s" % (SIGNAPK, _PEM, _PK8, _PATH, _RESULT_PATH)

    # Usage: signapk publickey.x509[.pem] privatekey.pk8 input output
    F_NULL = open(os.devnull, "w")
    proc = subprocess.Popen(_COMMAND, shell=True, stdout = F_NULL, stderr = subprocess.PIPE)

    while proc.poll() is None :
        loading_bar(0.1)
    
    F_NULL.close()
    
    if proc.returncode is 0 :
        print log("Signing sucesss!", 0)
        print log(_RESULT_PATH, 2)
    else :
        print log("Signing failed!", 1)
        


def inject_smali() :
    global DATA_AM_TRACER
    try :
        fp = open("./AM_Tracer.smali", "r")
        
        DATA_AM_TRACER = "# ========= Injected code by AM_Tracer[Start] =========\n\n" + \
            fp.read() + \
            "\n\n# ========= Injected code by AM_Tracer[End] =========\n\n"
        fp.close()
    except :
        print log("AM_Tracer.smali open failed, check file",1)
        return

    _INPUT_PATH = raw_input(log("Input directory or smali to patch >> ",3))

    if not os.path.exists(_INPUT_PATH) :
        print log("file doesn't exist! - ", 1)
        return
    
    if (os.path.splitext(os.path.basename(_INPUT_PATH))[1] == ".smali") or os.path.isdir(_INPUT_PATH) :
        recursive_search(_INPUT_PATH)
    else :
        print log("This file isn't smali or directory!", 1)
        return

## DFS
def recursive_search(DIR_PATH) :
    for obj in os.listdir(DIR_PATH) : 
        obj_path = "{}\\{}".format(DIR_PATH, obj)
        if os.path.isdir(obj_path) is True :
            # if filetype is directory, recur function
            recursive_search(obj_path)
        else :
            # ext is smali ?
            if os.path.splitext(obj_path)[1] in ".smali" :
                patch_smali(obj_path)


def patch_smali(FILE_PATH) :

    global DATA_AM_TRACER
    ## read smali data
    orignal_file = open(FILE_PATH, "r")
    data = orignal_file.read()
    orignal_file.close()

    ## parse class name
    class_name = data[:data.find("\n")].split()[-1]
    class_type = " ".join(data[:data.find("\n")].split()[:-1])
    
    ## exclude interface class, abstrcat class
    if "abstract" in class_type:
       return

    if "interface" in class_type:
       return

    
    ## check exception ## NO virtual methods keyword, NO Direct methods keyword
    idx = data.find("# virtual methods")
    if idx is -1 :
        print log("Virtual method isn't exist in (%s)" % (os.path.basename(FILE_PATH)), 2)
        return
    
    idx = data.find("# direct methods")
    if idx is -1 :
        print log("Direct method isn't exist in (%s)" % (os.path.basename(FILE_PATH)), 2)
        return
    
    
    ## Generate invoke string
    invoke = "invoke-static {}, %s->AM_Tracer()V" % (class_name)
   
    idx = idx + len("# direct methods") + 1    
    methods = data[idx:].split(".method ")[1:]
    patched_data = ""

    for obj in methods :
        func_type = " ".join(obj.split("\n")[0].split()[:-1])
        
        ## exclude abstract method
        if "abstract" in func_type:
            continue
        
        inject_idx = obj.find("\n")
        inject_invoke = ".method %s \n\t%s %s" % (obj[:inject_idx], invoke, obj[inject_idx:])
        patched_data = patched_data + inject_invoke 


    patched_data = data[:idx] + DATA_AM_TRACER + patched_data 
    patched_file = open(FILE_PATH, "w")
    patched_file.write(patched_data)
    patched_file.close()
    print log("Patch success (%s)" % (os.path.basename(FILE_PATH)), 2)




if __name__ == "__main__" :
    
    banner()
    
    while True :
        choice = raw_input(log("Slect menu >> ",3))
        if choice == "0" :
            unpack()
        elif choice == "1":
            rebuild()
        elif choice == "2":
            inject_smali()
        elif choice == "3":
            exit()
        else :
            continue
    