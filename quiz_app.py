from flask import Flask, request, jsonify, render_template
import models

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route("/", methods = ["GET"])
def index():
    return render_template("index.html")


@app.route("/user/", methods = ["GET", "DELETE", "POST"])
def user():
    session_details = request.json
    ##POST request adds a user to the users table
    if request.method=="POST":
        token = session_details["token"]
        if models.is_admin(token):
            retval = models.add_user(session_details["username"])
            return jsonify(retval)
        else:
            result = {"status":400, "errmesg":"Invalid token"}
            return jsonify(result), 400
    
    elif request.method == "DELETE":
        token = session_details["token"]
        if models.is_admin(token):
            retval = models.del_user(session_details["uid"])
            return jsonify(retval), retval["status"]
    elif request.method == "GET":
        retval = models.get_user_token(session_details["username"])
        return jsonify(retval), retval["status"]

    else:
        return jsonify({"status":400, "errmsg":"Invalid Request"}), 405

@app.route("/question/", methods=["POST", "DELETE"])
def question():
    qvalues = request.json
    token = qvalues["token"]
    if models.is_admin(token):
        if request.method == "POST":
            retval = models.add_question(qvalues)
            return jsonify(retval), retval["status"]
        elif request.method == "DELETE":
            retval = models.del_question(qvalues)
            return jsonify(retval), retval["status"]
    else:
        return jsonify({"status":403, "errmesg":"You are not admin"}), 403

@app.route("/quiz/", methods=["GET","POST"])
def quiz():
    q_entry = request.json
    token = q_entry["token"]
    quiz_id = q_entry["quiz_id"]
    if request.method == "GET":
        if (models.verify_session(token)):
            uid = models.get_user_id_from_token(token)
            retval = models.Quiz_Creator.render(quiz_id, uid)
            return jsonify(retval), 200
        else:
            return jsonify({"status":"400", "errmsg":"Invalid user token."}), 405
    elif request.method == "POST":
        answerkeys = q_entry["answerkeys"]
        if(models.verify_session(token)):
            retval = models.evaluate_score(answerkeys, quiz_id)        
            return jsonify(retval), retval["status"]
        else:
            return jsonify({"errmesg":"Invalid user token", "status":400}), 400


if __name__ == "__main__":
    app.run(debug=True)




