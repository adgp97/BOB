#!python 3.x
#################################################
## Author       : Jose Moran
## Github       : jose0796
## email        : jmoran071996@gmail.com
## file         : com.py 
## Description  : Library for digital and analog 
## unframing and processing for MC9S08QE128 uC
#################################################

def openPort(ports,baudrate=115200):

    """ Opens proper port from a given list
        :returns:
            A serial.Serial instance for the proper port
    """

    import serial
    for port in ports:
        s = serial.Serial(port,baudrate=baudrate,timeout=0.1)
        if s.read(4) != b'':
            return s
        

def listPorts(platform):

    """ Lists ports for specific platform
        :returns:
            A list of ports (strings)

    """


    import glob 
    import serial

    if platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif platform.startswith('linux') or platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsuported Platform')
    
    portList = []
    for port in ports:
        try: 
            s = serial.Serial(port,baudrate=115200,timeout=1)
            s.close()
            portList.append(port)
        except (OSError, serial.SerialException):
            pass
    
    return portList

def convertDigital(data, max=3):

    data_converted = int(data*(max))
    return data_converted


def convertAnalog(data, max=3, min=0, bitnum=12): 
    data_converted = float(data*(max-min)/(2**bitnum))
    return data_converted


def unframeData(frame,channel=1,digital=False):

    """ Unframe data received from serial port based on defined protocol 
    """

    if channel == 1:
        if not digital :
            return ((frame[0] & 0x3f) << 6 ) | (frame[1] & 0x3f)
        else: 
            return (frame[0] & 0x40) >> 6

    elif channel == 2:
        if not digital:
            return ((frame[2] & 0x3f) << 6 ) | (frame[3] & 0x3f)
        else:
            return (frame[1] & 0x40) >> 6


def synchronize(dataSerial):
    """ Synchronize data received from serial port
    """
    while(True):
        b = dataSerial.read(1)
        if ((b[0] & 0x8f) >> 7 ) == 0x00:
            garbage = dataSerial.read(3)
            break

def receiveData(dataSerial):
    
    frames = dataSerial.read(4)
    if ((frames[0] & 0x8f) >> 7) == 0 and ((frames[1] & 0x8f) >> 7) == 1 and ((frames[2] & 0x8f) >> 7) == 1 and ((frames[3] & 0x8f) >> 7) == 1 : 
        channelA1 = unframeData(frames)
        channelA2 = unframeData(frames,2)
        channelD1 = unframeData(frames,1,True)
        channelD2 = unframeData(frames,2,True)

        return channelA1,channelA2,channelD1,channelD2
    else: 
        synchronize(dataSerial)
        return 0,0,0,0


