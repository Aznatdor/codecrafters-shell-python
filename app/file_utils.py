import os

PATH = os.environ["PATH"]
PATH_LIST = PATH.split(os.pathsep)

def locate(fileName) -> str | None:
    """
        Locates executable file in directories defined in PATH variable
        
        ARGS:
            fileName: str - file name

        RETURNS:
            fullPath: str | None - full path if file is executable and None otherwise
    """

    if fileName in EXECUTABLES:
        return EXECUTABLES[fileName]

    return None

def findExes() -> dict[str, str]:
    """
        Finds all executible files listed in PATH directories

        RETURNS:
            executables: dict[str, str] - list absolute pathes to executable files
    """

    executables = {}

    for d in PATH_LIST:
        try:
            dirList = os.listdir(d)

            for file in dirList:
                fullPath = os.path.join(d, file)

                if os.path.isfile(fullPath) and os.access(fullPath, os.X_OK):
                    executables[file] = fullPath
        except: pass
    
    return executables


EXECUTABLES = findExes()
