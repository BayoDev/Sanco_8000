import serial
import serial.tools.list_ports
import os
from tqdm import tqdm


ser:serial.Serial = None
PORT_NAME = ""
BAUD_RATE = 0
TARGET_FOLDER = "./DATA/"

# Wait for ACK (0x06)
def wait_for_confirm():
    while 1:
            x = ser.read(1)
            if x == b'\x06' : return

def receive_file():
    data = []
    filename = []
    idx = 0
    print("Waiting for transmission to start")
    while 1:
            if ser.read(1) == b'\x02': break

    while 1:
        data.append([])
        filename.append("")
        # Get file name
        char_count = 0
        while 1:
                x = ser.read(1)
                if x==b'\x03' : break
                if x==b'\x20' :
                    char_count+=1
                    continue
                if char_count==8:
                    filename[idx]+="."
                filename[idx]+=str(x.decode('ascii'))
                char_count+=1
                ser.write(b'\x06')

        # Receive data
        print("Receiving file: "+filename[idx])
        is_ending = False
        b_count = 0
        c_count = 0
        while 1:
                x = ser.read(1)

                if c_count==16384+128:
                        c_count=0
                        ser.write(b'\x06')
                # Check for "control" bit
                if b_count == 128:
                        b_count = 0
                        if x==b'\x04': break
                        if x!=b'\x17' and not is_ending:
                            print(f"An error occured while reading the file")
                            exit()
                        continue
                
                data[idx].append(x)
                b_count+=1
                c_count+=1
        print("File received")
        idx+=1
        x = ser.read(1)
        # print(x)
        if x==b'\x17': 
            for i in range(516):
                 ser.read(1)
            x = ser.read(1)
        if x!=b'\x02' : break

    for i in range(len(data)):
        with open(TARGET_FOLDER+filename[i],'wb') as file:
                for c in data[i]:
                    file.write(c)
                print(f"{filename[i]} saved in {TARGET_FOLDER+filename[i]}")
    quit()

def send_file():
    global ser

    while 1:
        data = []
        file_name = ""
        file_extension = ""
        local_filename = ""

        while 1==1:
            local_filename = input(f"File to send (must be in dir '{TARGET_FOLDER}'): ")
            local_filename = TARGET_FOLDER+local_filename
            if os.path.isfile(local_filename):
                break
            print("File not found")

        while 1==1:
            file_name = input("CP/M file name (without extension): ")
            if len(file_name)>0 and len(file_name)<9:
                break
            print("The file name must be between 1 and 8 characters long")
        
        while len(file_name)!=8:
            file_name+=" "

        while 1==1:
            file_extension = input("CP/M file extension: ")
            if len(file_extension)==3:
                break
            print("The file extension must be 3 characters long")

        input("Press ENTER to start transmitting...")

        file_name+=file_extension
        data.append(b'\x02')
        for char in file_name:
                data.append(char.encode('ascii'))
        data.append(b'\x03')

        with open(local_filename,'rb') as file:
                b_count = 0
                while True:
                    if b_count==128:
                            b_count = 0
                            data.append(b'\x17')
                    x = file.read(1)
                    if x == b"":
                        break # end of file
                    data.append(x)
                    b_count +=1
                    

        if data[-1] == b'\x17' : data.pop() 
        else:
                while b_count<128:
                    b_count+=1
                    data.append(b'\x00')
        data.append(b'\x04')
        data.append(b'\x18')
        data.append(b'\x04')
        data.append(b'\x18')

        from tqdm import tqdm
        print(f"Sending file (size={len(data)} byte)")
        first_three = True
        p_count = -13
        for i in tqdm(range(len(data))):
                ser.write(data[i])
                if first_three and data[i] == b'\x03':
                        first_three = False
                        wait_for_confirm()
                if p_count==16384+128:
                        p_count=0
                        wait_for_confirm()
                if (ser.inWaiting() > 0):
                        x = ser.read(1)
                        print(f" {i} - {data[i]} - {x}")
                p_count+=1

        print("File sent")
        x = input("'Y' if you want to send another file, otherwise any other character: ")
        if x!="Y": break
        print("")
    quit()

def main():
    global ser

    print("\n\tSanco serial\n")

    # Get serial port
    ports = serial.tools.list_ports.comports()
    if len(ports) == 0:
        print("NO SERIAL PORTS AVAILABLE, ABORTING...")
        exit()
    print("Select a serial port:")
    for i in range(len(ports)):
        print(f"\t {i+1}) {ports[i]}")

    print("")
    sport = 0
    while sport<1 or sport>len(ports):
        try:
            sport = int(input(">>"))
        except:
            continue
    sport-=1

    PORT_NAME = ports[sport].name
    
    # Get baud rate
    while 1:
        try:
            BAUD_RATE = int(input("Baud rate:"))
        except:
            continue
        if BAUD_RATE>0:
            break


    # Open serial connection
    try:
        ser = serial.Serial(
            port=PORT_NAME,
            baudrate = BAUD_RATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
    except Exception as e:
        print("\nSomething went wrong while trying to open the serial port:\n\t"+str(e))
        quit()


    print("\n\tSelect mode:\n\n 1) Send program\n 2) Receive program\n")
    it = 0
    while it!=1 and it!=2:
        it = int(input(">>"))

    print("\nChecking for target folder...")
    if not os.path.isdir(TARGET_FOLDER):
        print("Target folder not found, creating...")
        try:
            os.mkdir(TARGET_FOLDER)
        except Exception as e:
            print(f"Something went wrong while trying to create the folder: {TARGET_FOLDER}:\n\t"+str(e))
            quit()
        print(f"Target folder '{TARGET_FOLDER}' created")
    else:
         print("Target folder found\n")

    if it==1:
        send_file()
    if it==2:
        receive_file()
    

if __name__ == '__main__':
    main()