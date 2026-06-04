
from flask import Flask, render_template, request
app = Flask(__name__)

def predict_score(study_hours, quiz, assignment, attendance, gpa):
    score = (
        0.15 * study_hours * 10 +
        0.30 * quiz +
        0.25 * assignment +
        0.20 * attendance +
        0.10 * (gpa * 25)
    )
    return round(min(score,100),1)

@app.route("/", methods=["GET","POST"])
def index():
    result = None
    cognitive = None
    if request.method == "POST":
        study = float(request.form["study_hours"])
        quiz = float(request.form["quiz"])
        assignment = float(request.form["assignment"])
        attendance = float(request.form["attendance"])
        gpa = float(request.form["gpa"])

        result = predict_score(study, quiz, assignment, attendance, gpa)
        cognitive = round((quiz + assignment + attendance)/3 * 1.2)

    return render_template("index.html", result=result, cognitive=cognitive)

if __name__ == "__main__":
    app.run(debug=True)
