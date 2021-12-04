import csv
import random
import sqlite3
from collections import OrderedDict

class Quiz_Creator():

    def __init__(self, nquestions=None, quizid=None, subject=None):
        self.nquestions = nquestions
        self.quizid = quizid
        self.subject = subject

    ## This function returns a randomised list of question ids from the questions database to create the quiz
    def formulate(self):
        count = 0
        question_id = []
        conn = sqlite3.connect("quiz.db")
        curr = conn.cursor()
        curr.execute("select max(qid) from questions")
        max = curr.fetchall()[0][0]

        while(count < self.nquestions):
            id = random.randint(1,max)
            if (id not in question_id):
                question_id.append(id)
                count+=1
            else:
                continue

        return question_id
        

    @classmethod
    def render(self, qid, uid=None, sort=False):
        conn = sqlite3.connect("quiz.db")
        curr = conn.cursor()
        curr.execute("select quizpaper from quiz where quiz_id = ?",(qid,))
        questions_id = curr.fetchall()[0][0]
        questions_id = questions_id.replace(",","").replace("[","").replace("]","").replace(" ", "")
        q_render = OrderedDict()
        questions_id = list(questions_id)
        count = 1
        for id in questions_id:
            curr.execute("select question, choice1, choice2, choice3, choice4 from questions where qid = ?", (id,))
            quizpaper = (curr.fetchall()[0])
            qno = "q" + str(count)
            question_entry = OrderedDict()
            question_entry = {"question":quizpaper[0], "choice1":quizpaper[1], "choice2":quizpaper[2], "choice3":quizpaper[3], "choice4":quizpaper[4]}
            q_render[qno] = question_entry
            count+=1
        try:
            curr.execute("insert into test_instance(quiz_id, user_id) values(?,?)", (qid, uid))
            conn.commit()
            conn.close()
        except sqlite3.Error as err:
            print("Err: ", err)
            conn.close()
            return {"err":err}
        return q_render

    @classmethod
    def sort_method(self, question_ids):
        # Question ids passed as an argument should be a list
        conn = sqlite3.connect("quiz.db")
        if conn is not None:
            cur = conn.cursor()
            ls_query_string = ','.join('?' for i in question_ids)
            sql_query = "SELECT qid FROM Questions WHERE qid IN (" + ls_query_string + ") order by marks desc, qid desc;"
            cur.execute(sql_query, question_ids)
            rows = cur.fetchall()
            sorted_question_ids = []
            for row in range(len(rows)):
                sorted_question_ids.append(rows[row][0])
            return sorted_question_ids

    #Imports csv data and pushes into quiz table
    @classmethod
    def import_file(self):
        questions = []
        with open("config/questions.csv", "r") as f:
            csv_reader = csv.reader(f, delimiter = ",")
            for row in csv_reader:
                questions.append(row)

        return questions
            





        