#!/usr/bin/python3
import os
import sys
import random
from shlex import split as parse_args
from shutil import which
def check_requirement(command:str):
    return which(command) is not None
def print_red(text):
    print("\033[31m"+text+"\033[0m")
def print_green(text):
    print("\033[32m"+text+"\033[0m")
tmpdirname = "/tmp/dofile-"+hex(random.randint(0,1000000))[2:]
data = """\
$$DATA$$
"""
functionblocks = {}#name: data
activefname = ""
activefdata = ""
requirements = []
docs = {}
main = ""
nad = False
private = False
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
    if not private:
        functionblocks[activefname] = activefdata
    if sch:
        activefdata = ""
os.mkdir(tmpdirname)
for it in functionblocks:
    with open(tmpdirname+"/"+it+".sh","w+") as f:
        f.write(functionblocks[it])
missingreq = []
for req in requirements:
    if not check_requirement(req):
        missingreq.append(req)
if len(missingreq) != 0:
    print_red(f"ERROR! The following dependencies were not met: {missingreq}")
    sys.exit(-1)
if len(sys.argv) == 2:
    if sys.argv[1] == "%list":
        dlist = [docs[z] for z in list(functionblocks.keys())]
        klist = [list(docs.keys())[list(functionblocks.keys()).index(x)] for x in list(functionblocks.keys())]
        maxn = max([len(d) for d in klist])
        print("Method name".ljust(maxn)+"|Description")
        for i in range(len(klist)):
            print(klist[i].ljust(maxn),dlist[i])
        sys.exit()
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
    else:
        print_green("Success!")
else:
    l = os.system(f"bash {tmpdirname}/{main}.sh")
    if l != 0:
        print_red("ERROR! Execution failed")
    else:
        print_green("Success!")