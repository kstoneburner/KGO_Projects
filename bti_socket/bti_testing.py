#CLIENT=[command]/[JOBnum]

 

#CLIENT=JOBSTART/EV6

#CLIENT=JOBPAUSE/EV6

#CLIENT=JOBRESUME/EV6

#CLIENT=JOBSTOP/EV6

 

import socket
import time


def run_crawl (command):

    HOST = '10.218.97.51' # The server's hostname or IP address
    PORT = 4085  # The port used by the server

    # Open Socket
    print('Opening Socket')

    try:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((HOST, PORT))

        sock.settimeout(3)

        print('Connected')

    except:

        print ('Connection failed.')

        sock.close()

        return None

 

 

 

 

    try:

        print('Sending:',command.encode())

        sock.send(command.encode())

    except:

        print('Sending command failed.')

 

    sock.close()

    print ('Closed Socket')
    return 

       

    try:

        print('Listening')

        rxdata = sock.recv(2048)

        print('Received', repr(rxdata))

    except:

        print('No Reply.')

 

        time.sleep(5)

 

       

    else:

       print('Skipped')

 

 

    sock.close()

    print ('Closed Socket')

 

 

 

 

 

 

## Mainline Code Starts Here!!!

 

 

#while True:

run_crawl('CLIENT=JOBSTART/NU105')
time.sleep(1)
run_crawl('CLIENT=JOBSTART/NU106')





#run_crawl('CLIENT=JOBPAUSE/EV6')

#run_crawl('CLIENT=JOBRESUME/EV6')

#run_crawl('CLIENT=JOBSTOP/EV6')



time.sleep(5)      

#input("press ENTER")

run_crawl('CLIENT=JOBSTOP/NU105')
run_crawl('CLIENT=JOBSTOP/NU106')
run_crawl('CLIENT=JOBSTOP/NU107')
