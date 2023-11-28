#!/usr/bin/python3

import os
import sys
import random
from shutil import which

def check_requirement(command:str):
    return which(command) is not None

if "--help" in sys.argv or "--version" in sys.argv:
    print("""
dofile (sbuild)
Simplistic bash-based build tool
Version 1.0

Usage: sbuild (method|--help|--version|%package)

--help          Prints help menu then exits
--version       Prints version info then exits

(nothing)       Looks for and executes main do file
(method)        if it exists, execute the specified method in the dofile
%package (out)  Package the dofile in the directory in to a portable python dofile
          """)
    sys.exit()

if not os.path.isfile(os.getcwd()+"/dofile"):
    print("ERROR! Failed to find dofile. Make sure you are in the same directory as the dofile.")
    sys.exit(-1)
else:
    tmpdirname = "/tmp/dofile-"+hex(random.randint(0,1000000))[2:]
    with open(os.getcwd()+"/dofile") as f:
        data = f.read()
    functionblocks = {}#name: data
    activefname = ""
    activefdata = ""
    requirements = []
    main = ""
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
            activefname = line.strip().split(" ")[1].split(":")[0]
            try:
                if line.strip().split(" ")[1].split(":")[1] == "admin":
                    nad = True
            except:
                pass
            sch = True
        else:
            if line.strip().startswith("!execute"):
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
                if os.path.getsize("template.py") > 2000 and os.path.getsize("template.py") < 3000:
                    with open("template.py") as f:
                        template = f.read()
                else:
                    print("ERROR! Failed to find template")
                    sys.exit(-1)
            with open(outfile,"w+") as f:
                f.write(template.replace("$$DATA$$",data))
            os.chmod(outfile,0o777)
            print("Success!")
            sys.exit()

    missingreq = []
    for req in requirements:
        if not check_requirement(req):
            missingreq.append(req)
    if len(missingreq) != 0:
        print(f"ERROR! The following dependencies were not met: {missingreq}")
        sys.exit(-1)
    if len(sys.argv) >= 2:
        rec = sys.argv[1]
        if not rec in functionblocks:
            print("ERROR! dofile does not contain the provided method")
            sys.exit(-1)
        l = os.system(f"bash {tmpdirname}/{rec}.sh")
        if l != 0:
            print("ERROR! Execution failed")
            sys.exit(l)
        else:
            print("Success!")
    else:

        if main == "":
            print("ERROR! dofile does not declare a main method")
            sys.exit(-1)
        #Execute
        l = os.system(f"bash {tmpdirname}/{main}.sh")
        if l != 0:
            print("ERROR! Execution failed")
            sys.exit(l)
        else:
            print("Success!")