import serial

port = serial.Serial(
        port = "/dev/ttyAMA0",
		baudrate = 57600,
		parity = serial.PARITY_NONE,
		stopbits = serial.STOPBITS_ONE,
		bytesize = serial.EIGHTBITS,
		timeout = 20
	    )

#現在使用中のチャンネルを確認する関数
def check_channel():
    print('Status  : Start ATmode')
    Enter_ATmode = '+++'
    Enter_ATmode = Enter_ATmode.encode()
    commands = [Enter_ATmode]
    for cmd in commands:
        port.write(cmd)
        response = port.read(2).decode()
        if response == 'OK' :
            print('Status  : Enter ATmode')
            check_CH = 'ATCH' + '\r'
            check_CH = check_CH.encode()
            commands = [check_CH]
            print('Status  : Check Channel')
            for cmd in commands:
                port.write(cmd)
                response = port.read(2).decode().strip()
                print('Channel :' , response)
        else:
                print('Status  : Failed')
                break
    port.close()

if __name__ == '__main__':
    check_channel()

