from flask import Flask,render_template,request,url_for,redirect

app=Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods =["GET", "POST"])
def login():
    if request.method=="POST":
        username=request.form.get('button')
        password=request.form.get('button')
        
    else:
        return render_template('login.html')




if __name__=="__main__":
    app.run(debug=True)