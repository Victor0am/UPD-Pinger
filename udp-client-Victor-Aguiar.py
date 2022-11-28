import time
from socket import *



# Host IP and port
serverHost = '168.227.188.22'
serverPort = 30000

# Create lists of sent and received messages to compare them
sentPacketsList = []
receivedPacketsList = []

# Create lists of times
rttsList = [] # list of rtt of each packet
initialTimeList = [] # list of the start timestamps of the requests
finalTimeList = [] # list of the final timestamps of the requests

# Total packets
totalPackets = 10

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Set timeout
serverSocket.settimeout(1) #set timeout of 1s

# mount a valid udp packet and then returns the packet
# a valid up packet contains 40 bytes that are used as following
####################################################################################################
#  Sequence number  #                 Type                 #  Timestamp (ms)  #  Packet's message  #
####################################################################################################
#      5 bytes      #  1 byte (0 for ping and 1 for pong)  #     4 bytes      #      30 bytes      #
####################################################################################################
def mount_udp_packet (number, message):
    # // is to convert ns = 10^-6ms  
    # % is to get the protocol number of digits of timestamp (4 bytes)
    timestamp_ms = (time.time_ns()//1000000) % 10000 
    return (str(number).zfill(5) + '0' + str(timestamp_ms) + message.ljust(30, '0'))


# checks if a received packet is valid
def check_if_received_packet_is_valid(received_packet):
    # Separate received_packet into objects of interest to compare
    rm_sequence_number = received_packet[0:5]
    rm_type = received_packet[5:6]
    rm_timestamp = received_packet[6:10]

    if len(received_packet) > 40 or rm_type != '1' or not rm_timestamp.isdigit() or not rm_sequence_number.isdigit():
        return False

    return True



for i in range(totalPackets):
    
    sentPacket = mount_udp_packet(i,'Victor Aguiar Marques') 
    sentPacketsList.append(sentPacket) 
    initialTimeList.insert(i+1, time.time_ns()) # store initial timestamp
    serverSocket.sendto(sentPacket.encode('utf-8'), (serverHost, serverPort)) #sends encoded packet



    try:
        receivedPacket, address = serverSocket.recvfrom(1024)
        receivedPacket = receivedPacket.decode('utf-8') # decodes packet
        finalTime = time.time_ns() # store final timestamp inside a variable
        
        while check_if_received_packet_is_valid(receivedPacket):
            receivedPacketsList.append(receivedPacket)
            rmSequenceNumber = receivedPacket[0:5]
            intSequenceNumber = int(rmSequenceNumber) # save a variable wit the int convertion of the sequence number

            # calculate rtt in ms using final - initial and then converts the results from ns to ms
            # then store the rtt
            rtt = (finalTime - initialTimeList[intSequenceNumber]) / 1000000 
            finalTimeList.insert(intSequenceNumber, finalTime)
            rttsList.append(rtt)

            # checks if the receivedPacket is from a previous timeout
            # if it is then try to receive another package (to complete the original request)
            if(intSequenceNumber < i):

                print(f"Delayed packet found (Packet {rmSequenceNumber}). RTT: " + str(rtt) + " ms.")   
                receivedPacket, address = serverSocket.recvfrom(1024)
                receivedPacket = receivedPacket.decode('utf-8') # decodes packet

            if intSequenceNumber == i: 
                print(f"Packet {rmSequenceNumber} RTT: " + str(rtt)+ " ms.")
                break

    except Exception as e:
        print("Timeout Error.")





totalPacketsDropped = totalPackets - len(receivedPacketsList) # Dropped = Total - Received
rttAverage = sum(rttsList)/len(receivedPacketsList) if len(receivedPacketsList) > 0 else 0
rttStandard = (sum([(x - rttAverage)**2 for x in rttsList])/10)**0.5 
print(f'{totalPackets} packets transmited, {len(receivedPacketsList)} received, {totalPacketsDropped/10*100:.2f}% packet loss, time {sum(rttsList):.2f}ms')
print(f'rtt min/avg/max/mdev = {min(rttsList):.2f}/{rttAverage:.2f}/{max(rttsList):.2f}/{rttStandard:.2f} ms') if len(rttsList) > 0 else print("All packets were lost.")
