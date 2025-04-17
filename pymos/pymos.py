



def listen_for_digi(input_port):   
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if input_port not in pc['active_ports']:
        pc['active_ports'].append(input_port)
    do_action("")
    
    PORT = input_port

    with soc as s:
        s.bind((HOST, PORT))
        s.listen()
        #pc["conn"], pc["addr"] 
        conn,addr = s.accept()
        print("=====")
        
        with conn: 
            pc['addr'].append(addr[0])
            if not clear_screen:
                print(f"Connected by {pc['addr']}")
                #print(pc["conn"])
               

            do_action("")
            do_ack = False
            while not pc["quit"]:
                # check for stop
                if not clear_screen:
                    print("-")
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    if not clear_screen:
                        print("Received: ", data)

                    handleInput(data)

                    #if not do_ack:
                    #    do_ack = True
                    #    conn.sendall(data)
                except:
                    pass

        #//*** Connection Closed 

        #//*** Close Local Side of Connection
        conn.close()

        #//*** Close the Socket
        s.close()

        #//*** Remove the Address from the Connected List
        pc['addr'].remove(addr[0])

        #//*** Start New Socket listener
        listen_for_digi(PORT)

        #//*** Destroy any remaining Resources
        return

def main:
	print("Hello World, This is the next step in MOS dominance")

if __name__ == "__main__":
	main()