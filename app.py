from flask import Flask, render_template,request,redirect,url_for
import pymysql

def get_db_connection():
    try:
        print("connecting to db")
        connection = pymysql.connect(
            host='mysql-35a2efd8-aleronpeterson-6630.l.aivencloud.com',
            user='avnadmin',
            password='AVNS_dzrOiUs7-uI2sv17LMW',
            database='defaultdb',
            port=19275,
            ssl={'ca': r'F:\Flask_Projects\E-library\certs\ca.pem'}
        )
        print("connected to db")
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


app=Flask(__name__)

@app.get("/")
def login():
    try:
        db=get_db_connection()
        if db is None:
            raise Exception("Database connection failed")
        cursor=db.cursor()
        cursor.execute("select * from user")
        users=cursor.fetchall()
        print(users)
        cursor.close()
        db.close()
        return render_template("login.htm",users=users)
    except Exception as e:
        print(f"Error: {e}")
        return render_template("error.htm")

@app.post("/")
def login_post():
    try:
        email=request.form.get("email")
        password=request.form.get("password")
        db=get_db_connection()
        if db is None:
            raise Exception("Database connection failed")
        cursor=db.cursor()
        cursor.execute("SELECT * FROM user WHERE email=%s AND password=%s", (email, password))
        user=cursor.fetchone()
        print(user)
        return redirect(url_for("index"))
        
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for("login"))

@app.get("/register")
def register():
    email=request.args.get("email")
    password=request.args.get("password")    # insert email and password into the database
    return render_template("register.htm",email=email)


@app.post("/register")
def register_post():
    email=request.form.get("email")
    password=request.form.get("password")
    # createa db connectionnn
    print("connecting to db")
    connection=get_db_connection()
    print("connected to db")
    if connection:
        cursor=connection.cursor()
        cursor.execute(''' insert into user (email,password) values (%s,%s)''',(email,password))
        connection.commit()
        print("User registered successfully!")
        cursor.execute("select * from user")
        user=cursor.fetchall()
        print(user)
        cursor.close()
        connection.close()
    else:
        print("connection failed")
    return redirect(url_for("register",email=email))

@app.get("/index")
def index():
    return render_template("index.htm")

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")