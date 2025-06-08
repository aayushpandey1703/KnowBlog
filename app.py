from flask import Flask, render_template,request,redirect,url_for,session,make_response
import pymysql
from loguru import logger
def get_db_connection():
    try:
        logger.debug("connecting to db")
        connection = pymysql.connect(
            host='mysql-35a2efd8-aleronpeterson-6630.l.aivencloud.com',
            user='avnadmin',
            password='AVNS_dzrOiUs7-uI2sv17LMW',
            database='defaultdb',
            port=19275,
            ssl={'ca': r'F:\Flask_Projects\Blog\certs\ca.pem'}
        )
        logger.debug("connected to db")
        return connection
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None


app=Flask(__name__)
app.secret_key="1234"

@app.get("/")
def login():
    try:
        email=request.args.get("email")
        return render_template("login.htm",email=email)
    except Exception as e:
        logger.error(f"Error: {e}")
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
        logger.info("Getting all users...")
        cursor.execute("select * from user")
        users=cursor.fetchall()
        for i in users:
            logger.info(i)
        cursor.execute("SELECT * FROM user WHERE email=%s AND password=%s", (email, password))
        user=cursor.fetchone()
        logger.debug(user)
        session['username']=user[1]
        return redirect(url_for("index"))
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return render_template("error.htm")

@app.get("/register")
def register():
    email=request.args.get("email")
    password=request.args.get("password")    # insert email and password into the database
    return render_template("register.htm",email=email)


@app.post("/register")
def register_post():
    try:
        username=request.form.get("username")
        email=request.form.get("email")
        password=request.form.get("password")
        # createa db connectionnn
        logger.debug("connecting to db")
        connection=get_db_connection()
        logger.debug("connected to db")
        if connection:
            cursor=connection.cursor()
            cursor.execute(''' insert into user (username,email,password) values (%s,%s,%s)''',(username,email,password))
            connection.commit()
            logger.debug("User registered successfully!")
            cursor.execute("select * from user")
            user=cursor.fetchall()
            logger.debug(user)
            cursor.close()
            connection.close()
        else:
            raise Exception("connection failed")
        return redirect(url_for("login",email=email))
    except Exception as e:
        logger.error(f"Error: {e}")
        return render_template("error.htm")

@app.get("/logout")
def logout():
    try:
        session.clear()
        return redirect(url_for("login"))
    except Exception as e:
        logger.error(f"Error: {e}")
        return render_template("error.htm")
        

@app.get("/index")
def index():
    username=session.get('username','Guest')
    return render_template("index.htm",username=username)

@app.get("/addblog")
def add_blog():
    try:
        if session:
            status=request.args.get('status')
            return render_template("addblog.htm",status=status)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        logger.error("Failed in add blog: "+str(e))
        return render_template("error.htm")

@app.post("/addblog")
def blog_post():
    try:
        title,content=request.form.get("title"),"content"
        author=session.get('username','Guest')
        conn=get_db_connection()
        if conn:
            cursor=conn.cursor()
            cursor.execute(f"insert into Blog (title,content,author) values ('{title}','{content}','{author}')")
            conn.commit()
            logger.debug("Blog add successfully")
            logger.debug("Getting all blogs..")
            blogs=cursor.execute("select * from Blog")
            logger.info(blogs)
            cursor.close()
            conn.close()
        else:
            raise Exception(f"failed to connect DB {conn}")

        return redirect(url_for("add_blog",status=True))
    except Exception as e:
        logger.error("Failed to add blog: "+str(e))
        return render_template("error.htm")
    


if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")