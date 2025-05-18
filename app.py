from flask import Flask, render_template,request,redirect,url_for
app=Flask(__name__)

@app.get("/")
def login():
    return render_template("index.htm")

@app.get("/register")
def register():
    email=request.args.get("email")
    password=request.args.get("password")
    return render_template("register.htm",email=email)


@app.post("/register")
def register_post():
    email=request.form.get("email")
    password=request.form.get("password")
    print(email,password)
    ## add email id and password to MySQL database
    return redirect(url_for("register",email=email))

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")