# sbuild-dofile
Simplistic bash-based build system

## For Users

### Installation

**YOU ONLY NEED THIS IF THE PACKAGE YOU WISH TO INSTALL HAS A `dofile` INSTEAD OF A PORTABLE DOFILE**

Download source code then extract. Open a terminal to the source directory. Run the following commands:

```
python3 do.py
sudo python3 do.py install
```
### Arguments
Arguments can only be passed to the dofile if a method is specialized rather than a main method. This is because there is currently no way to differentiate if what you are putting in is a method name or an argument

### Visual Studio Code Syntax Highlighting
This will be for both users and developers: If you want to have good syntax highlighting in Visual Studio code,

- Install the Custom Coloring plugin

- Copy this code:

```{"profileName":"dofile","keywords":[{"color":"#2eb28b","keywords":["!def","!execute","!main","!require"],"exact":false,"case":true},{"color":"#ff0000","keywords":[":admin",":private"],"exact":true,"case":true},{"color":"#901414","keywords":["!def %package","!def %list"],"exact":false,"case":true}],"ranges":[]}```

## For Developers!

### Statements

Thank you so much for considering Dofile for your project's build system. There are four keywords: !def, !execute, !main, and !require. The sbuild system is based off of methods. Each method is its own bash file, and thus has its own set of variables and functions. !def declares a new method. The code runs from !def to either the next !def or the end of the file. The code inside of the method is pure and perfect bash syntax. Directories, variables, and functions are preserved within the method. !execute can only be declared within the body of a method. !execute executes another method. !execute can provide arguments. For example `!execute abc def 123` will execute method abc with arguments def and 123. !main declares a main method. The !main statement must be at the top of the file. For example `!main run` will set the method `run` to the main method. The main method is executed automatically if no specific method is provided by the user.!require is declared at the top as well. It declares required programs that are verified before any method is run.

### Tags

Next, there are tags. Tags are added directly onto a def statement as follows:

```
!def methoda
#No tags

!def methodb:tag
#One tag

!def methodc:tag1:tag2
#Multiple tags
```

As of v4, there are two tags in sbuild: `admin` and `private`

admin declares that the method requires root permissions to run. 

private declares that the method will ignored in a packaged "portable dofile"

### Docs

On the !def line, you can also add a short description after the name and tags, like so: [The description MUST be in quotes]
```
!def mymethod "My method does stuff and things"

#Or

!def anothermethod:admin "This method also does stuff"
```