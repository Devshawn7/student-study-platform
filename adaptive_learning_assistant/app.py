from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def predict_score(study_hours, quiz, assignment, attendance, gpa):
    # Optimize calculation:
    # 0.15 * study_hours * 10 -> 1.5 * study_hours
    # 0.10 * (gpa * 25) -> 2.5 * gpa
    score = (
        1.5 * study_hours +
        0.30 * quiz +
        0.25 * assignment +
        0.20 * attendance +
        2.5 * gpa
    )
    # Ensure prediction is bounded between 0.0 and 100.0
    return round(min(max(score, 0.0), 100.0), 1)

def get_cognitive_score(quiz, assignment, attendance):
    # Average of quiz, assignment, and attendance, scaled by 1.2
    # Ensure it's capped at 100 and non-negative
    raw_cognitive = (quiz + assignment + attendance) / 3.0 * 1.2
    return int(round(min(max(raw_cognitive, 0.0), 100.0)))

def validate_and_clamp_inputs(data):
    """
    Validates and clamps inputs to reasonable ranges.
    Returns a dict of parsed values or raises ValueError.
    """
    try:
        study = float(data.get("study_hours", 0))
        quiz = float(data.get("quiz", 0))
        assignment = float(data.get("assignment", 0))
        attendance = float(data.get("attendance", 0))
        gpa = float(data.get("gpa", 0))
    except (ValueError, TypeError):
        raise ValueError("All inputs must be valid numbers.")

    # Clamp bounds to ensure reasonable ranges
    study = min(max(study, 0.0), 50.0)            # Study hours: 0-50 hrs/week
    quiz = min(max(quiz, 0.0), 100.0)             # Quiz score: 0-100
    assignment = min(max(assignment, 0.0), 100.0)   # Assignment score: 0-100
    attendance = min(max(attendance, 0.0), 100.0)   # Attendance: 0-100%
    gpa = min(max(gpa, 0.0), 4.0)                # GPA: 0.0-4.0

    return {
        "study_hours": study,
        "quiz": quiz,
        "assignment": assignment,
        "attendance": attendance,
        "gpa": gpa
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    cognitive = None
    error = None
    
    # Default inputs for initial page load or values to preserve in standard form submit
    inputs = {
        "study_hours": 10.0,
        "quiz": 80.0,
        "assignment": 80.0,
        "attendance": 90.0,
        "gpa": 3.0
    }

    if request.method == "POST":
        is_json = request.is_json
        
        if is_json:
            data = request.get_json() or {}
        else:
            data = request.form

        try:
            cleaned = validate_and_clamp_inputs(data)
            inputs.update(cleaned)
            result = predict_score(
                cleaned["study_hours"],
                cleaned["quiz"],
                cleaned["assignment"],
                cleaned["attendance"],
                cleaned["gpa"]
            )
            cognitive = get_cognitive_score(
                cleaned["quiz"],
                cleaned["assignment"],
                cleaned["attendance"]
            )
            
            if is_json:
                return jsonify({
                    "status": "success",
                    "result": result,
                    "cognitive": cognitive
                })
        except ValueError as e:
            error = str(e)
            if is_json:
                return jsonify({
                    "status": "error",
                    "message": error
                }), 400

    return render_template("index.html", result=result, cognitive=cognitive, error=error, **inputs)

if __name__ == "__main__":
    app.run(debug=True)
