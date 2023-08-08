from flask import Flask, render_template
import pyodbc
app = Flask(__name__)




rundown_names = ["5PM Weekday"]

def get_db_connection():
    h_name = socket.gethostname()
    HOST = socket.gethostbyname(h_name)
    PORTS = [10522]

    if os.path.exists(config_filename):
        print("Process Config File")
        with open(config_filename) as f:
            for line in f:
                
                #//*** strip out everything after # comment
                if "#" in line:
                    line = line.split("#")[0]


                #//*** Look for lines with values:
                if "=" in line:

                    key,value = line.split("=")

                    #//*** Strip all whitespace from key & value
                    key = key.strip()
                    value = value.strip().replace("\n","")

                    print(f">{key}<")
                    print(f">{value}<")

                    if key == "server":
                        config['server'] = value

                    if key == "database":
                        config['database'] = value


    cnxn = pyodbc.connect('Trusted_Connection=yes;DRIVER={SQL Server};SERVER='+config['server']+';DATABASE='+config['database']+';UID=user;PWD=password')
    print("!!!!!!")
    return cnxn

@app.route('/')
def index():
    print("INDEX!")
    cnxn = get_db_connection()

    print(cnxn)

    query = f"""
    SELECT *
    FROM resourceReservations 
    WHERE startTime BETWEEN {date_range}
    AND content LIKE '%{rundown_target}%'
    """
    #WHERE stationId = '1132'

     
    #//*** Get List of Rundowns Matching date Range and Rundown Name
    cursor.execute(query)
    results = cursor.fetchall()

    
    #posts = conn.execute('SELECT * FROM posts').fetchall()
    cnxn.close()
    #return render_template('index.html', posts=results)
    return "Hello Wrodl"

app.run()