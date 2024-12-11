import prompt
import pyodbc

g = {
    "quit" : False,
    "api_root" : "/api/v1/",
    "token" : None,
    'token_expires_at' : None,

    'load_pcr' : {
        "source_id" : None,
        "ro_api" : "ro/",

    },
    'dalet' : {
        'server' : None,
        'database' : None,
        'username' : None,
        'password' : None


    },
    'cue_type' : ['PGM','PST'],
    'clients' : { },

}


print("Beginning Tests: ")
print("Loading Config File:")
prompt.load_configfile() 
g = prompt.g

print(g)

print("Testing SQL Connection:")
server = g['dalet']['server']
database = g['dalet']['database']
username = g['dalet']['username']
password = g['dalet']['password']

print(f"Server: {server}")
print(f"Database: {database}")
print(f"Username: {username}")
print(f"Password: {password}")

#cnxn = pyodbc.connect('Trusted_Connection=yes;DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

connectionString = f'Trusted_Connection=yes;DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
connectionString = f'Trusted_Connection=yes;DRIVER={{SQL Server}};SERVER={server};DATABASE={database};'
cnxn = pyodbc.connect(connectionString) 
#cursor = cnxn.cursorpassword
cnxn.close()
print("Connect to Dalet Database: SUCCESSFULL")

