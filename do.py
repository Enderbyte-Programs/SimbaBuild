#!/usr/bin/python3

import os
import sys
import random
from shutil import which
from shlex import split as parse_args

def check_requirement(command:str):
    return which(command) is not None

def print_red(text):
    print("\033[31m"+text+"\033[0m")

def print_green(text):
    print("\033[32m"+text+"\033[0m")

if "--help" in sys.argv or "--version" in sys.argv:
    print("""
dofile (simbabuild)
SIMplistic BAsh-based BUILD tool
Version 4

Usage: sbuild [method|--help|--version|%package|%list] (args)

--help          Prints help menu then exits
--version       Prints version info then exits

(nothing)           Looks for and executes main do file. Notice! Args can't be passed to a default method
(method) (*args)    if it exists, execute the specified method in the dofile with the optional args
%package (out)  Package the dofile in the directory in to a portable python dofile
%list           List all methods with a short description
          """)
    sys.exit()

if not os.path.isfile(os.getcwd()+"/dofile"):
    print_red("ERROR! Failed to find dofile. Make sure you are in the same directory as the dofile.")
    sys.exit(-1)
else:
    tmpdirname = "/tmp/dofile-"+hex(random.randint(0,1000000))[2:]
    with open(os.getcwd()+"/dofile") as f:
        data = f.read()
    functionblocks = {}#name: data
    docs = {}#name: doc
    activefname = ""
    activefdata = ""
    requirements = []
    main = ""
    private = False
    nad = False
    for line in data.splitlines():
        
        if nad:
            activefdata += "if [ \"$EUID\" -ne 0 ]; then\n echo \"This method needs root.\"\n exit 2 \nfi\n"
        sch = False
        nad = False
        if line.strip() == "" or line.strip().startswith("#"):#Remove empty lines and comments
            continue
        elif line.strip().startswith("!main"):
            main = line.strip().split(" ")[1]
            continue
        elif line.strip().startswith("!require"):
            for req in line.strip().split(" ")[1:]:
                if req.strip() == "":
                    continue
                requirements.append(req)
            continue
        #iter
        if line.strip().startswith("!def"):
            private = False
            
            activefname = parse_args(line.strip())[1].split(":")[0]
            prx = parse_args(line.strip())
            if len(prx) > 2:
                docs[activefname] = prx[2]
            else:
                docs[activefname] = "(no documentation)"
            tags = parse_args(line.strip())[1].split(":")
            if "admin" in tags:
                nad = True
            if "private" in tags:
                private = True
            sch = True
        else:
            if line.strip().startswith("!execute"):
                if len(line.strip().split(' ')) > 2:
                    activefdata += f"bash {tmpdirname}/{line.strip().split(' ')[1]}.sh {' '.join(line.strip().split(' ')[2:])}\n"
                else:
                    activefdata += f"bash {tmpdirname}/{line.strip().split(' ')[1]}.sh\n"
            else:
                activefdata += line.strip() + "\n"

        functionblocks[activefname] = activefdata

        if sch:
            activefdata = ""
    os.mkdir(tmpdirname)
    for it in functionblocks:
        with open(tmpdirname+"/"+it+".sh","w+") as f:
            f.write(functionblocks[it])
    if len(sys.argv) == 3:
        if sys.argv[1] == "%package":
            outfile = sys.argv[2]
            if os.path.isfile("/usr/lib/do/template.py"):
                with open("/usr/lib/do/template.py") as f:
                    template = f.read()
            elif os.path.isfile("template.py"):
                if os.path.getsize("template.py") > 3000 and os.path.getsize("template.py") < 4000:
                    with open("template.py") as f:
                        template = f.read()
                else:
                    print_red("ERROR! Failed to find template")
                    sys.exit(-1)
            with open(outfile,"w+") as f:
                f.write(template.replace("$$DATA$$",data))
            os.chmod(outfile,0o777)
            print_green("Exportation completed without errors")
            sys.exit()
    if len(sys.argv) == 2:
        if sys.argv[1] == "%list":
            dlist = [docs[z] for z in list(functionblocks.keys())]
            klist = [list(docs.keys())[list(functionblocks.keys()).index(x)] for x in list(functionblocks.keys())]
            maxn = max([len(d) for d in klist])
            print("Method name".ljust(maxn)+"|Description")
            for i in range(len(klist)):
                print(klist[i].ljust(maxn),dlist[i])
            sys.exit()

    missingreq = []
    for req in requirements:
        if not check_requirement(req):
            missingreq.append(req)
    if len(missingreq) != 0:
        print_red(f"ERROR! The following dependencies were not met: {missingreq}")
        sys.exit(-1)
    if len(sys.argv) >= 2:
        rec = sys.argv[1]
        if not rec in functionblocks:
            print_red("ERROR! dofile does not contain the provided method")
            sys.exit(-1)
        if len(sys.argv) >= 3:
            l = os.system(f"bash {tmpdirname}/{rec}.sh {' '.join(sys.argv[2:])}")
        else:
            l = os.system(f"bash {tmpdirname}/{rec}.sh")
        if l != 0:
            print_red("ERROR! Execution failed")
            sys.exit(l)
        else:
            print_green("Success!")
    else:

        if main == "":
            print_red("ERROR! dofile does not declare a main method")
            sys.exit(-1)
        #Execute
        l = os.system(f"bash {tmpdirname}/{main}.sh")
        if l != 0:
            print_red("ERROR! Execution failed")
            sys.exit(l)
        else:
            print_green("Success!")