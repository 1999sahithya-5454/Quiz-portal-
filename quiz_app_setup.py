import sqlite3
import secrets

conn = sqlite3.connect("quiz.db")
curr = conn.cursor()
admin_token = secrets.token_hex(5)

try:
    curr.execute("pragma foreign_keys = on;")
    curr.execute("create table if not exists users(uid int primary key, name varchar(255), token varchar(255))")
    curr.execute("create table if not exists questions(qid int primary key, question varchar(1000) unique, "
                 "choice1 varchar(255), choice2 varchar(255), choice3 varchar(255), choice4 varchar(255), key int, "
                 "marks int, remarks varchar(255))")
    curr.execute("insert into users(uid, name, token) values(?,?,?)",(10000, "admin", admin_token))
    curr.execute("create table if not exists quiz(quiz_id int primary key, quizpaper varchar(2000), answerkeys "
                 "varchar(255))")
    curr.execute("create table if not exists test_instance(id integer primary key autoincrement, quiz_id int, "
                 "user_id int, foreign key(quiz_id) references quiz(quiz_id), foreign key(user_id) references users("
                 "uid))")
    conn.commit()
except sqlite3.Error as err:
    print("Failed to create table: ", err)
finally:
    if conn:
        conn.close()
        print("Closed connection")   

