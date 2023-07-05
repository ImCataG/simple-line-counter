import os
import sys
import platform

class Comments:
    singleLine = []
    multiLine = {}

    def __init__(self, singleLine, multiLine):
        self.singleLine = singleLine
        self.multiLine = multiLine
    
class Count:
    codeOnly = 0
    commentOnly = 0
    mixed = 0
    blank = 0
    notcounted = 0
    notredable = 0
    def __init__(self, codeOnly=0, commentOnly=0, mixed=0, blank=0, notcounted=0, notreadable=0):
        self.codeOnly = codeOnly
        self.commentOnly = commentOnly
        self.mixed = mixed
        self.blank = blank
        self.notcounted = notcounted
        self.notreadable = notreadable

    def __repr__(self):
        return f"Code Only: {self.codeOnly}; Comment Only: {self.commentOnly}; Mixed: {self.mixed}; Blank: {self.blank}; NC: {self.notcounted}; NR: {self.notreadable}."

    
    def __str__(self):
        return f"Code Only: {self.codeOnly}\nComment Only: {self.commentOnly}\nMixed: {self.mixed}\nBlank: {self.blank}\nNot Counted: {self.notcounted}\nNot Readable: {self.notreadable}"
    
class File:

    def __init__(self, name, path):
        self.name = name
        self.path = path
        if name.split(".")[-1] not in extensionlookup.keys():
            self.filetype = "other"
        else:
            self.filetype = extensionlookup[name.split(".")[-1]]

        if self.filetype == "other":
            self.count = Count(0, 0, 0, 0)
        self.count = plscount(path, self.filetype)

    def __repr__(self):
        return f"File({self.name}, {self.filetype}, {self.count.__repr__()})"
    
    def __str__(self):
        return f"Name: {self.name}\nFiletype: {self.filetype}\n{self.count}"
    
class Directory:

    def __init__(self, name, path):
        self.name = name
        self.path = path
        
        self.files = []
        self.directories = []
        if name == '.git' or name == '.github' or name == '.vscode' or name == '__pycache__':
            self.count = Count(0, 0, 0, 0, 0, 0)
            return

        # get all files in directory
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                self.files.append(File(file, os.path.join(path, file)))
        # get all directories in directory
        
        for directory in os.listdir(path):
            if os.path.isdir(os.path.join(path, directory)):
                self.directories.append(Directory(directory, os.path.join(path, directory)))
        # get all counts
        self.count = Count()
        for file in self.files:
            self.count.codeOnly += file.count.codeOnly
            self.count.commentOnly += file.count.commentOnly
            self.count.mixed += file.count.mixed
            self.count.blank += file.count.blank
            self.count.notcounted += file.count.notcounted
            self.count.notreadable += file.count.notreadable

        for directory in self.directories:
            self.count.codeOnly += directory.count.codeOnly
            self.count.commentOnly += directory.count.commentOnly
            self.count.mixed += directory.count.mixed
            self.count.blank += directory.count.blank
            self.count.notcounted += directory.count.notcounted
            self.count.notreadable += directory.count.notreadable

    def output(self, depth):
        ans = "\t" * depth + self.name + " -> " + self.count.__repr__() + "\n"
        if self.files:
            ans += "\t" * (depth+1) + "Files:\n"
            for file in self.files:
                ans += "\t" * (depth+1) + file.name + " -> " + file.count.__repr__() + "\n"

        if self.directories:
            ans += "\t" * (depth+1) + "Directories:\n"
            for directory in self.directories:
                ans += directory.output(depth + 1)
        return ans

def plscount(path, filetype):
    comm = commentlookup[filetype]
    with open(path, 'r') as f:
        if not f.readable():
            return Count(0, 0, 0, 0, 0, 1)
        #print(f"Counting {path}")
        try:
            lines = f.readlines()
        except:
            print(f"WARNING: Could not read {path}")
            return Count(0, 0, 0, 0, 0, 1)
        codeOnly = 0
        commentOnly = 0
        mixed = 0
        blank = 0
        inComment = False
        for line in lines:
            currentNonComment = False
            currentComment = False
            line = line.strip()
            if line == "":
                blank += 1
                continue

            for i in range(len(line)):
                foundLineComment = False
                if not inComment:
                    for single in comm.singleLine:
                        if line[i:min(len(line)-1, i+len(single))].startswith(single):
                            if currentNonComment:
                                mixed += 1
                            else:
                                commentOnly += 1

                            foundLineComment = True
                            break
                    if foundLineComment:
                        break
                    for multiStart in comm.multiLine.keys():
                        if line[i:min(len(line)-1, i+len(multiStart))].startswith(multiStart):
                            inComment = True
                            currentComment = True
                            break
                    currentNonComment = True
                else:
                    for multiEnd in comm.multiLine.values():
                        if line[i:min(len(line)-1, i+len(multiEnd))].startswith(multiEnd):
                            inComment = False
                            currentComment = True
                            break
                    currentComment = True

            if not foundLineComment:
                if currentComment and currentNonComment:
                    mixed += 1
                elif currentComment:
                    commentOnly += 1
                elif currentNonComment:
                    codeOnly += 1

            
        if filetype == "other":
            return Count(0, 0, 0, blank, codeOnly, 0)
        return Count(codeOnly, commentOnly, mixed, blank)

extensionlookup = {'c' : 'C', 'cpp' : 'C++', 'h' : 'C / C++ header or similar', 'py' : 'Python', 'java' : 'Java', 'rs' : 'Rust', 'sh' : 'Shell'}
commentlookup = {'other' : Comments([],{}), 'C' : Comments(['//'], {'/*' : '*/'}), 'C++' : Comments(['//'], {'/*' : '*/'}), 'C / C++ header or similar' : Comments(['//'], {'/*' : '*/'}), 'Python' : Comments(['#'], {}), 'Java' : Comments(['//'], {'/*' : '*/'}), 'Rust' : Comments(['//'], {'/*' : '*/'}), 'Shell' : Comments(['#'], {})}

if __name__ == "__main__":
    splitter = "/"
    if platform.system() == "Windows":
        splitter = "\\"
    else:
        splitter = "/"
    # if no args given, use current directory
    target = os.getcwd()
    
    # if args given, use first arg as target
    if len(sys.argv) > 1:
        target = sys.argv[1]

    # if target is a file, count it and output
    if os.path.isfile(target):
        print(File(target.split(splitter)[-1], target))
    
    # if target is a directory, count it and output

    elif os.path.isdir(target):
        print(Directory(target.split(splitter)[-1], target).output(0))
    