import threading,socket,time

PORTS = [10540,10541]
h_name = None
HOST = None
h_name = socket.gethostname()
HOST = socket.gethostbyname(h_name)
    
g = {
    'active_ports' : [], #//*** Holds the active MOS PORTS. Avoids double mounting
    'addr' : [], #//*** Active Connection List (Might be Legacy)
    'quit' : False,
    'packets_in' : [],
}


def listen_for_digi(input_port):   
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if input_port not in g['active_ports']:
        g['active_ports'].append(input_port)
    
    PORT = input_port

    with soc as s:
        s.bind((HOST, PORT))
        s.listen()
        #pc["conn"], pc["addr"] 
        conn,addr = s.accept()
        print("=====")
        whole_packet = ""
        print("Pre-Conn")
        with conn: 
            g['addr'].append(addr[0])
            #if not clear_screen:
            #    print(f"Connected by {pc['addr']}")
            #    #print(pc["conn"])
               

            #do_action("")
            do_ack = True
            while not g["quit"]:
                # check for stop
                #if not clear_screen:
                #    print("-")
                try:
                    #//*** Receive 1024 of data. It's expected to be a partial Packet
                    data = conn.recv(1024)
                    #print("Raw Received: ", data)

                    #//*** Convert the Byte arra to a UTF8 String.
                    #//*** Add to the whole packet
                    whole_packet += data.decode('utf-8', errors="replace")
                    print("XXXXXXXXXXXXXXXXXX")

                    #//*** Write Back on the connection to acknowledge it
                    #//*** Probably need something more formal
                    #//*** Or maybe need to roAck the Completed Packet
                    conn.write("")
                    

                    #//*** If </mos> in whole_packet, then pack is complete
                    #//*** Send Whole Packet to g['packets_in']
                    #//*** Reset WholPacket for connection reuse
                    if "</mos>" in whole_packet:
                        print(whole_packet)
                        g['packets_in'].append(whole_packet)
                        whole_packet = ""
                        print(g['packets_in'])


                    
                    if not data:
                        break
                    #if not clear_screen:
                    #    print("Received: ", data)

                    #handleInput(data)

                    #if not do_ack:
                    #    do_ack = True
                    #    conn.sendall(data)
                except:
                    print("Problem Processing Packet. Skipping it. Will need additional error handing code if this pops up.")
                    pass

        #//*** Connection Closed 

        #//*** Close Local Side of Connection
        conn.close()

        #//*** Close the Socket
        s.close()

        #//*** Remove the Address from the Connected List
        g['addr'].remove(addr[0])

        #//*** Start New Socket listener
        listen_for_digi(PORT)

        #//*** Destroy any remaining Resources
        return

def main():



    print("Hello World, This is the next step in MOS dominance")
    #//*** Build a listener for each port in PORTS
    for port in PORTS:
        print(f"Spinning up Listener: {port}")
        listener = threading.Thread(target = listen_for_digi, args=[port])
        listener.daemon = True
        listener.start()
        time.sleep(.5)

    while True:
        time.sleep(.1)
if __name__ == "__main__":
	main()