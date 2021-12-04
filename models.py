from sqlite3.dbapi2 import SQLITE_OK
from quiz_creator import Quiz_Creator
import secrets
import sqlite3



def is_admin(token):
    conn = sqlite3.connect("quiz.db")
    curr = conn.cursor()
    try:
        curr.execute("select token from users where name = 'admin'")
        admin_token = curr.fetchall()[0][0]
        if token == admin_token:
            print(f"Admin token verified: {admin_token}")
            conn.close()
            return True
        else:
            print(admin_token)
            conn.close()
            return False
            
    except sqlite3.Error as err:
        print("Error: ", err)
        return False

def verify_session(token):
    conn = sqlite3.connect("quiz.db")
    curr = conn.cursor()
    curr.execute("select token from users")
    tokens = list((curr.fetchall()))
    for t in tokens:
        tokens[tokens.index(t)] = t[0]
    conn.close()
    
    if token in tokens:
        return True
    else:
        return False    


def add_user(username):
    conn = sqlite3.connect("quiz.db")
    curr = conn.cursor()
    try:
        token = secrets.token_hex(5)
        curr.execute("select max(uid) from users")
        uid = curr.fetchall()[0][0]
        uid+=1
        if(uid > 11000):
            conn.close()
            return {"status": 507, "errmesg":"Max user limit exceeded"}
        else:
            curr.execute("insert into users(uid, name, token) values(?, ?, ?)", (uid, username, token))
            conn.commit()
            conn.close()
            return {"status":200, "errmsg":"", "user":uid, "token":token} 
    except sqlite3.Error as err:
        print("Error: ", err)
        return {"status": 200, "errmsg":err}


def del_user(uid):
    if uid == 10000:
        return{"status":403, "errmesg":"Forbidden. Cannot delete admin"}
    try:
        conn = sqlite3.connect("quiz.db")
        curr = conn.cursor()
        curr.execute("delete from users where uid = ?", (uid,))
        conn.commit()
        conn.close()
        return{"status":200, "info":f"{uid} deleted"}
    except sqlite3.Error as err:
        print("Error: ", err)
        conn.close()
        return {"status": 400, "errmesg": err}

def get_user_id_from_token(token):
    conn = sqlite3.connect("quiz.db")
    curr = conn.cursor()
    try:
        curr.execute("select uid from users where token = ?", (token,))
        uid = curr.fetchall()[0][0]
        conn.close()
        return int(uid)
    except sqlite3.Error as err:
        print("Err : ", err)
        return None

def get_user_token(username):
    conn = sqlite3.connect("quiz.db")
    curr = conn.cursor()
    try:
        curr.execute("select token from users where name = ?", (username,))
        token = curr.fetchall()[0][0]
        conn.close()
        return {"status":200, "token":f"{token}"}
    except sqlite3.Error as err:
        print("Error: ", err)
        conn.close()
        return {"status":200, "errmesg":err}


def add_question(q_entry):
    conn = sqlite3.connect("quiz.db")
    curr = conn.cursor()
    curr.execute("select max(qid) from questions")
    max_id = curr.fetchall()[0][0]
    try:
        id = max_id + 1
        curr.execute("insert into questions(qid, question, choice1, choice2, choice3, choice4, key, marks) values(?,?,?,?,?,?,?,?)",(id, q_entry["question"], q_entry["choice1"], q_entry["choice2"], q_entry["choice3"], q_entry["choice4"], q_entry["key"], q_entry["marks"] ))
        conn.commit()
        conn.close()
        return {"status":200, "info":f"question inserted successfully, qid = {id}"}
    except sqlite3.Error as err:
        print("Error: ", err)
        conn.close()
        return {"status": 200, "errmsg":err}

def del_question(q_entry):
    conn = sqlite3.connect("quiz.db")
    curr = conn.cursor()
    id = q_entry["qid"]
    try:
        curr.execute("delete from questions where qid = ?", (id,))
        conn.commit()
        conn.close()
        id = q_entry["qid"]
        return {"status":200, "info":f"question {id} deleted successfully"}
    except sqlite3.Error as err:
        print("Err: ", err)
        conn.close()
        return{"status":200, "errmesg":err}



def add_questions_from_file():
    conn = sqlite3.connect("quiz.db")
    curr = conn.cursor()
    questions = Quiz_Creator.import_file()
    try:
        id = 1
        for q in questions[1:]:
            curr.execute("insert into questions(qid, question, choice1, choice2, choice3, choice4, key, marks, remarks) values(?,?,?,?,?,?,?,?,?)", (id, q[0],q[1],q[2],q[3],q[4],q[5],q[6],""))
            id+=1
        
        conn.commit()
        conn.close()
    except sqlite3.Error as err:
        print("Error: ", err)
        return {"status": 200, "errmsg":err}



def generate_quiz(nq):
    quiz = Quiz_Creator(nq)
    conn = sqlite3.connect("quiz.db")
    curr = conn.cursor()
    keys = []
    question_id = quiz.formulate()
    
    for q in question_id:
        curr.execute("select key from questions where qid = ?",(q,))
        keys.append(curr.fetchall()[0])
    
    curr.execute("select max(quiz_id) from quiz")
    id = curr.fetchall()[0][0]
    id += 1
    try:
        curr.execute("insert into quiz (quiz_id, quizpaper, answerkeys) values(?,?,?)", (id, str(question_id), str(keys)))
        conn.commit()
        conn.close()
        print("Quiz added to table")
    except sqlite3.Error as err:
        print("Error : ", err)
    


def evaluate_score(answerkeys, quiz_id):
    try:
        conn = sqlite3.connect("quiz.db")
        curr = conn.cursor()
        #get the answer keys from table quiz
        curr.execute("select answerkeys from quiz where quiz_id = ?", (quiz_id,))
        keys = curr.fetchall()[0][0]
        keys = list(keys.replace(",","").replace("[","").replace("]","").replace(" ", "").replace("(", "").replace(")",""))
        #Fetch the questions from the quiz
        curr.execute("select quizpaper from quiz where quiz_id = ?", (quiz_id,))
        questions = curr.fetchall()[0][0]
        questions = list(questions.replace(",","").replace("[","").replace("]","").replace(" ", "").replace("(", "").replace(")",""))
        #Fetch the marks per question for each quiz
        marks = []
        for q in questions:
            curr.execute("select marks from questions where qid = ?", (q,))
            marks.append(curr.fetchall()[0][0])
        #evaluate the submitted keys with the keys from the database
        result = []
        score = 0
        max_score = 0
        if len(answerkeys)<=len(keys):
            for i in range(len(answerkeys)):
                max_score += marks[i]
                if (int(answerkeys[i])==int(keys[i])):
                    result.append(1)
                    score+=marks[i]
                else:
                    result.append(0)
                    score += 0
            conn.close()
            return {"result":result, "score":score, "max_score":max_score, "status":200}
        else :
            conn.close()
            return {"result":"Incorrect Keys", "status":200}
    except sqlite3.Error as err:
        print("Error: ", err)
        conn.close()
        return {"errmesg":err}
        




## This function adds questions from the csv file. Uncomment this function to add questions from csv file
#add_questions_from_file()

## To generate a quiz, uncomment the function below and pass the number of questions in the quiz as an argument
#generate_quiz(4)








