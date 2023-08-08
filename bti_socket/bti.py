#//*** Validate IP Address
#https://codefather.tech/blog/validate-ip-address-python/


#python bti.py 10.218.97.51 4085 START NU105
#python bti.py 10.218.97.51 4085 STOP NU105,NU106,NU107
 

import socket,time,sys
import argparse
import ipaddress


#HOST = '10.218.97.51' # The server's hostname or IP address
#PORT = 4085  # The port used by the server

parser = argparse.ArgumentParser(description="Connect to BTI Crawl")
parser.add_argument('ip', type=str, help="IP Address of BTI Device") 
parser.add_argument('port', type=str, help="Listening Port on BTI Device") 
parser.add_argument("START_STOP", type=str, help="[START/STOP] to Start or Stop a Job")
parser.add_argument("JOB", type=str, help="BTI JOB Value. Separate multiple jobs with a comma.Example: NU105,NU106,NU107")

#parser.add_argument("tank", type=str)
args = parser.parse_args()


#//********************************
#//********************************
#//**** INPUT VALIDATION
#//********************************
#//********************************
try:
    
    #//*** Validate Ip Address
    ipaddress.ip_address(args.ip)
    print("Valid IP address:",args.ip)
    ip = args.ip

except:
    print("INVALID IP Address: ", args.ip)
    sys.exit()


try:
    #//*** Validate Port Value
    port = int(args.port)

    if port >= 1 and port <= 65535:
        print("Valid Port:",port)
    else:
        print("INVALID PORT value",port," -- Value must be betwen 1 - 65535")
except:
    print("INVALID PORT Value")


action = args.START_STOP.upper()

#//**************************
#//*** Validate START STOP
#//**************************
if action != "START" and action != "STOP":
    print("After IP and Port declare START_STOP. Enter START or STOP only!!\nInput Value:",args.START_STOP.upper())
    sys.exit()

jobs = args.JOB
print("JOB Value: ",jobs)




#//********************************
#//********************************
#//**** OPEN CONNECTION
#//********************************
#//********************************

print('Opening Socket')

try:

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((ip, port))

    sock.settimeout(3)

    print('Connected')

except:

    print ('Connection failed. Quitting')

    sock.close()
    sys.exit()
    


#//********************************
#//********************************
#//**** BUILD COMMAND
#//********************************
#//********************************

#'CLIENT=JOBSTOP/NU105'

for job in jobs.split(","):

    command = f"CLIENT=JOB{action}/{job}"
    print(command)


    #//********************************
    #//********************************
    #//**** SEND COMMAND
    #//********************************
    #//********************************

    try:

        print('Sending:',command.encode())

        sock.send(command.encode())

    except:

        print('Sending command failed.')
        sock.close()
        print ('Closed Socket')
        sys.exit()

    #//********************************
    #//********************************
    #//**** Wait for response
    #//********************************
    #//********************************
    try:

        print('Listening')

        rxdata = sock.recv(2048)

        print('Received', repr(rxdata))

    except:

        print('No Reply.')

time.sleep(1)
print('Close and Quitting')
sock.close()
sys.exit()



#print(parser.parse_args() )
#print(parser.parse_args(["ip"]) )


 


 


 

## Mainline Code Starts Here!!!

 

 

#while True:

#run_crawl('CLIENT=JOBSTART/NU105')
#time.sleep(1)
#run_crawl('CLIENT=JOBSTART/NU106')







#time.sleep(5)      

#input("press ENTER")

#run_crawl('CLIENT=JOBSTOP/NU105')
#run_crawl('CLIENT=JOBSTOP/NU106')
#run_crawl('CLIENT=JOBSTOP/NU107')
