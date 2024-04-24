# <div align="center"> Sanco 8000 serial utilities </div>

 This pyton script allows you to send and receive programs to/from a Sanco 8000 computer using its CP/M utilities RCX62 and TRX62.

❗ It's now possible to receive multiple file❗

You can receive all files by setting the script in receive mode and select everything ("\*.\*") in TRX62.

# Transmission description from receiving end
>Note that if at any moment the transmitter receives 0x0D the transmission  is considered failed and must start from the beginning

When the program RCX62 is started it enters the MAIN_LOOP. 

## MAIN_LOOP

While inside the MAIN_LOOP the program will keep reading incoming characters from the serial port until one of three values are received:

- 0x18 : signals RCX62 to close the program (no more files to receive)
- 0x02 : A file is about to be transmitted and RCX62 enters the RECEIVE_MODE
- 0x12 : ?

## RECEIVE_MODE
1) When in this mode RCX62 will read 12 bytes from the serial port containing 8 bytes for the file name, 3 bytes for the extension and the last byte that needs to be 0x03 (end of text). 

2) If no error occurs RCX62 will send back an acknowledge (0x06).

3) The program will then start to receive the actual data of the file by entering in the DATA_LOOP

### DATA_LOOP

The program will read 128 blocks of 128 bytes from the serial port. After each block it expects one of two characters:

- 0x04 indicating that it was the last block  (saving the file and going back to the MAIN_LOOP)
- 0x17 used as an acknowledgment (keep going through the DATA_LOOP)

After 128 blocks are received (without a 0x04) the programs will send and acknowledgment (0x06) to the transmitter when it's ready to receive another 128 blocks of data and starts over the DATA_LOOP
