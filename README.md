# FileSystem

This filesystem only used a single root directory.
The format of the filesystem is detailed below:
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
