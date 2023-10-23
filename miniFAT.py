'''

Name: EddyM10

Class: CSCI-3341-001

Date: 04-25-23

Filename: miniFAT.py

Description: This file will provide a interface
             for a custom file system
'''
import sys
import os

#==============Globals Variables==============
fileSystem: str = ""

#==============Functions==============

#-------------command()-------------
'''
    This function will take in a command from the
    user to execute that command function
    
    Pre: string userCommand

    Post: executes the function of the command or
          error message
'''
def command(userCommand : str):
        
        
        if len(userCommand) > 1 :
            nameArg : str =  userCommand[1].replace(" ", "")
        
        try:
            match userCommand[0]:
                case "ls": ls(nameArg)
                case "mkfile": mkfile(nameArg)
                case "delete": delete(nameArg)
                case "read" : readFile(nameArg)
                case "quit": sys.exit()
                case _: print("UNKNOWN COMMAND OR NO ARGUMENT")
        except Exception:
            print("VALID COMMAND HAS VALID NO FLAG OR ARGUMENT")
       
       
#-------------ls()-------------
'''
    This function will display the files in a 
    directory
    
    Pre: a string argument

    Post: no return, prints the list of 
          files/directories
'''  
def ls(flag: str):
        
        match flag:
                case "-all": curr(True);curr(False)
                case "-curr": curr(True)
                case "-del": curr(False)
                case _: print("UNKOWN FLAG")

#-----------curr()--------------
'''
    This function will be show the current file/directories
    in the FAT not deleted or current deleted files

    Pre: boolean

    Post: prints non deleted files/directories or deleted files depending on
          pre boolean
'''
def curr(nonDeleted: bool):
      
    fs = open(fileSystem, 'rb')
    fs.seek(256, 0)
    tempHex: str = ""
    
    #reads files names within the first cluster that 
    # stores the info
    i = 0
    while(i < 1024):
        tempHex: bytes = fs.read(1)
       
        if(tempHex.hex() == "7e" and nonDeleted):
            fs.seek(7, 1)
        elif(tempHex.hex() != "7e" and not nonDeleted):
             fs.seek(7, 1)
        else:

            #prints only for non empty file space 
            firstLetter: str = fs.read(1).decode("ascii")
            if(firstLetter != "~"):
                 print(tempHex.decode("ascii"), end="")
                 print(firstLetter, end="")

            for j in range(0, 3):  
                letter: str = fs.read(1).decode("ascii")
                if not letter == "~":
                    print(letter, end="")

            print(end=" ")
            fs.seek(3, 1)

        i += 8 

    print()            
    fs.close()

#-------------mkfile()-------------
'''
    This function will make a new file inside the file system
    from a users current directory copying the file contents
    passed in the argument
    
    Pre: a string name

    Post: no return, file is made inside the file system
'''  
def mkfile(name: str):
    
    freeClustersSize: int = 0
    isSpaceFree: bool = False
    clusters: list  = []
    nextCluster: bytes

    #get file size
    try:
        fileSize = os.path.getsize(name)
    except:
        print("FILE NOT FOUND")
        return
    
    #checks if file size is too big for file system representation 
    #of two bytes max
    if(fileSize > 65536):
         print("File is too big to represent in two bytes")
         return

    
    #open files
    fs = open(fileSystem, 'rb+')
    userFile = open(name, 'rb+')

    #check if enough clusters are avaliable for file
    for i in range(0,256):
        nextCluster = fs.read(1)
        
        if(nextCluster.hex() == "00"):
            freeClustersSize += 1024
            clusters.append(i)

        if(freeClustersSize >= fileSize):
            isSpaceFree = True
            break

    #start for space available in the file system
    #and mark clusters for file storage
    if(isSpaceFree):
        tempBytes :bytes
        j:int  = 0

        for cluster in clusters:
            fs.seek(cluster, 0)

            #last cluster for file is marked with an eof byte
            if(clusters[-1] == cluster):
                fs.write(b'\xff')
                
            else:
                tempBytes = clusters[j + 1].to_bytes(1, 'big')
                fs.write(tempBytes)
                  
            j+=1    
    else:
        print("Not Enough Space for file")
        fs.close()
        userFile.close()
        return
    
    #change the File Allocation Table to add new file info
    fs.seek(256, 0)
    shortName :bytes= bytes(name[:5],"raw_unicode_escape")
    k:int = 0
    while(k < 1024):
        tempHex = fs.read(1)
        if(tempHex.hex() == "7e"):
            
            fs.seek(-1, 1)
            fs.write(shortName)
            fs.write(clusters[0].to_bytes(1, "big"))
            fs.write(fileSize.to_bytes(2,"big"))
            #could use something like num.to_bytes((num.bit_length() + 7)) for no fix arg
            break
        else:        
            fs.seek(7, 1)
            k += 8

    #start to write file contents to file system 
    nextCluster = clusters[0].to_bytes(1, "big")
    writeSize:int  = 0
    while(nextCluster.hex() != 'ff'):

            clusterLoc: int = int(nextCluster.hex(), 16) 
            tempNum: int = 1024 * clusterLoc + 256
            fs.seek(tempNum, 0)

            for i in range(0,1024):

                #checks to see only file size is read
                if writeSize >= fileSize:
                    break

                userFileContent: bytes = userFile.read(1)
                fs.write(userFileContent)
                writeSize += 1
        
            
            fs.seek(clusterLoc, 0)
            nextCluster = fs.read(1)
            fs.seek(0,0)
            

    userFile.close()
    fs.close()
   

#-------------delete()-------------
'''
    This function will delete a file in the file system
    
    Pre: a string name

    Post: no return, file is deleted
'''  
def delete(fName: str):
      
    fs = open(fileSystem, 'rb+')
    fs.seek(256, 0)
    tempHex: bytes = ""
    tempFileName: str = ""
    clusterNum: bytes

    #searches if file exists
    i = 0
    while(i < 1024):
        tempHex = fs.read(1)
        
        if(tempHex.hex() == "7e"):
            fs.seek(7, 1)
        else:
            tempFileName = tempHex.decode("ascii") + fs.read(4).decode("ascii")
            
            #file is found
            #denoting first byte name to ~ in File
            #Allocation Table
            if(fName == tempFileName):
                clusterNum = fs.read(1)
                fileSize: int = int (fs.read(2).hex(), 16)
                fs.seek(-8, 1)
                
                fs.write(b'\x7e')
                fs.close()
                #zeros out the clusters for deleted file
                deleteHelper(clusterNum)
                return
            else:
                fs.seek(3, 1)   
        i += 8 
    
    fs.close()
    print("FILE NOT FOUND")

#--------deleteHelper()-----------
'''
    This function will help the delete function
    
    Pre: starting cluster bytes

    Post: no return, file is deleted from the File
          Allocation Table
'''  
def deleteHelper(startingCluster: bytes):
    
    nextCluster: bytes = startingCluster
    fs = open(fileSystem, 'rb+')

    #reads the clusters for the deleted file to be changed
    #to zeros
    while(nextCluster.hex() != 'ff'):

        clusterLoc: int = int(nextCluster.hex(), 16) 
        fs.seek(clusterLoc, 0)
        nextCluster = fs.read(1)
        fs.seek(-1 , 1)
        fs.write(b'\x00')
        fs.seek(0,0)

    
    print()
    fs.close()
     

#-------------readFile()-------------
'''
    This function will display the file contents
    
    Pre: a string name

    Post: no return, file contents is displayed
'''  
def readFile(fileName: str):

    fs = open(fileSystem, 'rb')
    fs.seek(256, 0)
    tempHex: bytes = ""
    tempFileName: str = ""
    clusterNum: bytes
    deletedFile = False

    #check deleted file
    if(fileName[0] == "~"):
         deletedFile = True

    #searches if file exists
    i = 0
    while(i < 1024):
        tempHex = fs.read(1)
        
        if(tempHex.hex() == "7e" and not deletedFile):
            fs.seek(7, 1)
        elif(tempHex.hex() != "7e" and deletedFile):
             fs.seek(7,1)
        else:
            tempFileName = tempHex.decode("ascii") + fs.read(4).decode("ascii")
            
            #file is found
            if(fileName == tempFileName):
                clusterNum = fs.read(1)
                fileSize: int = int (fs.read(2).hex(), 16)
                fs.close()
                fileFound(clusterNum, fileSize, deletedFile)
                #print("File name is :", fileName)
                #print(clusterNum)
                return
            else:
                fs.seek(3, 1)   
        i += 8 

    fs.close()
    print("FILE NOT FOUND")

#-------------fileFound()-------------
'''
    This function is a helper and will display the file contents
    of the file founded 
    
    Pre: a starting cluster(bytes) number, and file size

    Post: no return, file contents is displayed
'''  
def fileFound(startingCluster: bytes, fileSize: int, deletedFile: bool):
    
    readSize: int = 0
    nextCluster: bytes = startingCluster
    fs = open(fileSystem, 'rb')

    #reads the clusters for the file/deleted file
    if(not deletedFile):
        while(nextCluster.hex() != 'ff'):

            clusterLoc: int = int(nextCluster.hex(), 16) 
            tempNum: int = 1024 * clusterLoc + 256
            fs.seek(tempNum, 0)

            for i in range(0,1024):
                #checks to see only file size is read
                if readSize >= fileSize:
                    break
            
                print(fs.read(1).decode(encoding="ascii", errors="replace"), end="")
                readSize += 1
        
            fs.seek(0,0)
            fs.seek(clusterLoc, 0)
            nextCluster = fs.read(1)
            fs.seek(0,0)
    elif(deletedFile):
        clusterLoc: int = int(startingCluster.hex(), 16)
        
        while(readSize < fileSize or clusterLoc != 256):
          
            fs.seek(clusterLoc, 0)
            nextCluster = fs.read(1)
            fs.seek(0,0)

            if(nextCluster.hex() == "00" ):
                tempNum: int = 1024 * clusterLoc + 256
                fs.seek(tempNum, 0)

                for i in range(0,1024):

                    #checks to see only file size is read
                    if readSize >= fileSize:
                        break
            
                    print(fs.read(1).decode(encoding="ascii", errors="replace"), end="")
                    readSize += 1

            clusterLoc += 1
           
    
    print()
    fs.close()

#-------newFileSystem()-------
'''
    This function will make a new file system and start it

    Pre: name string

    Post: new file system is made, if already exists the file system
          will still be used for shell

'''
def newFileSystem(fsName: str):
    global fileSystem
    fileSystem  = fsName

    try:
        file = open(fsName, "x")
        file.close()
    except Exception as e:
        print(e)
        return
    
    #format the new file system
    file = open(fsName, "rb+")
    file.write(b'\xff')
    file.seek(254,1)
    file.write(b'\xff')
    clusterZero: bytes =b'\x7e\x7e\x7e\x7e\x7e\x00\x00\x00'
    for i in range(0,128):
        file.write(clusterZero)

    #fills with empty space (zeros)
    for j in range(0, 32640):
        
        file.write(bytes(8))


    file.close()
    

#==============Main==============
if __name__ == "__main__":
      
       #sets what file system to open
        if "-fs" in sys.argv:
            index = sys.argv.index("-fs")
            value = sys.argv[index + 1]
            fileSystem = value
        
        #makes a new file system
        if "-new" in sys.argv:
            index = sys.argv.index("-new")
            value = sys.argv[index + 1]
            newFileSystem(value)

        #waits for commands and flags
        while(True):
            print("root?>" , end=" ")
            userCommand: str = input()
            commandArg : list = userCommand.split(" ")
            command(commandArg)

    
        

                
        
             
