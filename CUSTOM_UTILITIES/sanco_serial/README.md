# <div align="center"> Sanco 8000 serial utilities </div>

 This pyton script allows you to send and receive programs to/from a Sanco 8000 computer using its CP/M utilities RCX62 and TRX62.

❗ It's now possible to receive multiple file❗

You can receive all files by setting the script in receive mode and select everything ("\*.\*") in TRX62.

# Transmission description from receiving end

## Header

1. The sender start the transmission by sending a **START OF TEXT** character (0x02). 

2. The sender transmit 8 bytes containing the file name, if it's shorter than 8 characters the remaining bytes are set to 0x20 (" "). 

3. The sender transmit 3 bytes containing the extension of the file.

4. The sender transmit an **END OF TEXT** and wait for the receiver to send an **ACKNOWLEDGEMENT** (0x06)

## Data

5. The sender start transmitting the data
    - every 128 bytes of data the sender transmits either a:
        - (0x04) This is the only way to end the transmission, 0x00 are added when needed to align the 0x04 to the 128th byte. After that another byte 0x18 is sent and the transmission end.
        - (0x17) This is used for "control" purposes, if the receiver doesn't receive this control byte a **TRANSMISSION ERROR** is raised.

    - every 16KiB (16384 bytes) of data (without considering the control bytes 0x17) the sender stop the transmission and waits for an ackowledgement (0x06) from the receiver before resuming the transmission.

