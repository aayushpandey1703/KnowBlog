from flask import Flask, render_template,request,redirect,url_for,session,make_response
import pymysql
from loguru import logger
import uuid,datetime

def get_db_connection():
    try:
        logger.debug("connecting to db")
        connection = pymysql.connect(
            host='mysql-35a2efd8-aleronpeterson-6630.l.aivencloud.com',
            user='avnadmin',
            password='AVNS_dzrOiUs7-uI2sv17LMW',
            database='defaultdb',
            port=19275,
            ssl={'ca': r'/app/certs/ca.pem'}
        )
        logger.debug("connected to db")
        return connection
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None


app=Flask(__name__)
app.secret_key="1234"

@app.get("/login")
def login():
    try:
        email=request.args.get("email")
        message=request.args.get("message")
        next_page=request.args.get("next")
        return render_template("login.htm",email=email,message=message,next_page=next_page)
    except Exception as e:
        logger.error(f"Error: {e}")
        return render_template("error.htm")

@app.post("/login")
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
        if user is None:
            return redirect(url_for("login",message="Invalid email id"))
        logger.debug(user)
        # create session and store session in cookie
        session_uid=str(uuid.uuid4())
        session[session_uid]={}
        session[session_uid]['username']=user[1]
        session[session_uid]['email']=user[2]
        # next page 
        next_page=request.args.get('next')
        print(next_page)
        # make response for custom header and cookie
        response=make_response(redirect(next_page or url_for("index")))
        response.set_cookie("cookie_name",session_uid,max_age=3600)
        return response
        
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
        session_uid=request.cookies.get('cookie_name')
        session.pop(session_uid)
        response=make_response(redirect(url_for("login")))
        response.set_cookie('cookie_name','',max_age=0)
        return response
    except Exception as e:
        logger.error(f"Error: {e}")
        return render_template("error.htm")
        

@app.get("/")
def index():
    session_uid=request.cookies.get('cookie_name',None)
    if session_uid:
        username=session[session_uid]['username']
    else:

        username="Guest"
    conn=get_db_connection()
    if conn:
        cursor=conn.cursor()
        cursor.execute("select * from Blog order by id desc")
        blogs=cursor.fetchall()
        blog_list=[]
        for i in blogs:
            dt=i[4]
            formatted=dt.strftime('%B %d, %Y')
            blog_card={
                "id":i[0],
                "title":i[1],
                "content":i[2],
                "author":i[3],
                "date":formatted
            }
            print(blog_card)
            blog_list.append(blog_card)
    else:
        raise Exception("Failed to connect to database")
    return render_template("index.htm",username=username,blogs=blog_list)


@app.get("/addblog")
def add_blog():
    try:
        session_uid=request.cookies.get('cookie_name')
        if session_uid:
            status=request.args.get('status')   
            return render_template("addblog.htm",status=status)
        else:
            logger.error("No session")
            logger.error(session_uid)
            return redirect(url_for("login"))
    except Exception as e:
        logger.error("Failed in add blog: "+str(e))
        return render_template("error.htm")

@app.post("/addblog")
def blog_post():
    try:
        title,content=request.form.get("title"),request.form.get("content")
        session_uid=request.cookies.get('cookie_name')
        if session_uid is None:
            raise Exception("no session ID found")
        author=session[session_uid]['username']
        conn=get_db_connection()
        if conn:
            cursor=conn.cursor()
            cursor.execute(f"insert into Blog (title,content,author) values ('{title}','{content}','{author}')")
            conn.commit()
            logger.debug("Blog add successfully")
            logger.debug("Getting all blogs..")
            cursor.execute("select * from Blog")
            allblogs=cursor.fetchall()
            logger.info(allblogs)
            cursor.close()
            conn.close()
        else:
            raise Exception(f"failed to connect DB {conn}")

        return redirect(url_for("add_blog",status=True))
    except Exception as e:
        logger.error("Failed to add blog: "+str(e))
        return render_template("error.htm")

@app.get("/view_blog")
def viewblog():
    session_uid=request.cookies.get("cookie_name")
    blog_id=request.args.get("q")
    try:
        # check if session exsts
        if (session_uid) and (session_uid in session):
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute(f"select * from Blog where id='{blog_id}'")
            blog=cursor.fetchone()
            dt=blog[4]
            formatted_date=dt.strftime("%B %d, %Y")
            blog_details={
                "title":blog[1],
                "content":blog[2],
                "author":blog[3],
                "created_at":formatted_date
            }
            return render_template("viewblog.htm",blog=blog_details)
        else:
            return redirect(url_for("login",next=f"/view_blog?q={blog_id}"))
    except Exception as e:
        logger.error(f"Failed to get blog: {str(e)}")
        return render_template("error.htm")

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")