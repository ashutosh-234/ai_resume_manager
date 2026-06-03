from flask import Flask ,render_template , request, redirect , session
from ai import analyze_resume
from db import Base ,  engine , sessionLocal 
import models 
from PyPDF2 import PdfReader
import docx
import json

app = Flask (__name__)
app.secret_key = "secret123"

Base.metadata.create_all(bind = engine)


#HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect ("/dashboard")
    return redirect("/login")

#SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup ():
    db= sessionLocal()

    if request.method == "post":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db.query(models.user).filter_by(email=email).first
        if existing_user:
            return "iser already exists"
        
        user = models.user(email=email , password = password)
        db.add(user)
        db.commit()

        return redirect("/login")
    
    return render_template("signup.html")


#LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    db = sessionLocal()

    if request.method == "post":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(models.user).filter_by(email=email,password=password)

        if user:
            session["user"] = user.email
            return redirect("/dashboard")
        else:
            return "invalid credentials"
        
    return render_template("login.html")
        

#DASHBOARD
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect ("/login")
    
    result = None

    if request.method =="POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")

        file = request.files.get("file")

        #file handling
        if file and file.name != "":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PdfReader(file)
                    text = ""
                    for pages in pdf_reader.pages:
                        text += pages.extract_text()or ""
                    resume_text = text 
                except Exception as e:
                    result = {"error": f"PDF error: {str(e)}"}

            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text +"\n"
                    resume_text = text
                except Exception as e:
                    result = {"error:" f"Docx error {str(e)}"}

        if resume_text and user_goal:
            try:
                result = analyze_resume(resume_text, user_goal)

                #save to db
                db = sessionLocal()
                user =  db.query(models.user).filter_by(email=session["user"]).first()

                report = models.reports(
                    user_id = user.id,
                    resume_text = resume_text,
                    result = json.dumps(result)
                )

                db.add(report)
                db.commit()

            except Exception as e:
                result = {"error": f"AI error:{str(e)}"}
        return render_template(
            "dashboard.html",
            user = session["user"],
            result = result
        )

#history
@app.route("/history")
def history():
    if "User" not in session:
        return redirect ("/login")
    
    db = sessionLocal()
    user = db.query(models.user).filter_by(email=session["user"]).first()

    reports = db.query(models.reports).filter_by(user_id = user.id).all()

    #convert json string > dict
    pasred_reports = []
    for r in reports:
        try:
            pasred_results = json.loads(r.result)
        except:
            pasred_results = []

        pasred_reports.append({
            "resume":r.resume_text,
            "result":pasred_results
        })

    return render_template("history.html", reports= pasred_reports)

# logout route

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect ("/login")




if __name__ == "__main__":
    app.run (debug=True)




    # mysql+mysqldb://Q5mxVhbZH4EQPQC.root:JBppJUmArdpH1rm2@gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com:4000/test?ssl_mode=VERIFY_IDENTITY&ssl_ca=<CA_PATH>
    # pass  ---- JBppJUmArdpH1rm2