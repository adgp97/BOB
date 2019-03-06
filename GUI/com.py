#!python 3.x
#################################################
## Author       : Jose Moran
## Github       : jose0796
## email        : jmoran071996@gmail.com
## file         : com.py 
## Description  : Library for digital and analog 
## unframing and processing for MC9S08QE128 uC
#################################################


def convertDigital(data, max=3, min=0, bitnum=1):
    data_converted = int(data*(max))
    return data_converted


def convertAnalog(data, max=3, min=0, bitnum=12): 
    data_converted = float(data*(max-min)/(2**12))
    return data_converted


def unframeData(frame,channel=1,digital=False):
    
    if channel == 1:
        if not digital :
            return ((frame[0] & 0x3f) << 6 ) | (frame[1] & 0x3f)
        else: 
            return (frame[0] & 0xb0) >> 7
    elif channel == 2:
        if not digital:
            return ((frame[2] & 0x3f) << 6 ) | (frame[3] & 0x3f)
        else:
            return (frame[1] & 0xb0) >> 7


def synchronize(dataSerial):
    
    while(True):
        b = dataSerial.read(1)
        if ((b[0] & 0x8f) >> 7 ) == 0x00:
            garbage = dataSerial.read(3)
            break

def startReceiving(dataSerial):
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


