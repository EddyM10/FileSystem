# FileSystem

This filesystem only used a single root directory.
### The format of the filesystem is detailed below:
    • The first 256 bytes of the file is the FAT table.
    • Files are written in cluster sizes of 1024 bytes.
    • The FAT uses 1 byte per cluster on the system.
    • The FAT is the only thing to not take up a full cluster.
    • Cluster 0 is the root directory and starts at offset \x100
    • Directory structure:
        ◦ 8 bytes per file
            ▪ 5 bytes are the name
            ▪ 1 byte for the starting cluster
            ▪ 2 bytes for the file size
    • Total Filesize is 256 + (256*1024)
        ◦ First 256 is the FAT
        ◦ There are 256 clusters each of size 1024 bytes, hence the 256*1024
        ◦ Total siz3e 257 KB
    • Cluster 0 is reserved so a byte of \x00 is used to denote a free cluster
    • The end of file character is \xff
    • A deleted file has the first character of the filename replace with a ~

# Input and Output

        Input: 
        
         $python3.11 miniFat.py -new newFileSystem.fs(empty file system same functionality as the flag -fs)
         $python3.11 miniFat.py -fs fileSystem.fs(file system already created)
         
         1. roo?> ls -all
         2. root?> ls -curr
         3. root?> ls -del
         4. root?> read yo.txt
         5. root?> read ~il.t
         6. root?> delete Fi3.t
         7. root?> mkfile HelloFile.txt
         8. root?> quit
         9. root?> what(Invalid Command)

        
         Output:
         
         1. Proje Fi3.t
             ~il.t
         2. Proje Fi3.t
         3. ~il.t
         4. I am in the text file (File content)
         5. You found me (Deleted File Content)
         6. No output (Deletes file in file system by changing the asssociated clusters to 0 and changing the first byte of the name to ~ , example ~i3.t)
         7. No output (File is added to the file system check "ls -curr", overwrites empty FAT space or deleted file)
         8. Program stops execution
         9. UNKNOWN COMMMANDS OR UNKOWN FLAG(Error message)

# Usage

1) Open a terminal to run the file program, then enter the following sequences:
2) $python3.11 miniFAT.py -fs Custom.fs
3) root?> (Enter Command)
4) Commands with flags or without flags include: ls -all, ls -curr, ls -del, mkfile <name>, delete <name>,read <file>, quit

Further Note:<br>  * Mkfile takes a file already made in your directory and makes a new file inside the file system.<br>
      * $python3.11 miniFAT.py -new newCustom.fs will just be an empty file system with the commands usable

         
