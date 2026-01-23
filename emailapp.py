from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import pymysql
import os

from QuantumEncryption import computeQuantumKeys, quantumEncryptMessage, quantumDecryptMessage

username = ""


def UserLogin(request):
    return render(request, 'UserLogin.html')


def UserLoginAction(request):
    global username
    if request.method == "POST":
        uname = request.POST.get("t1")
        pwd = request.POST.get("t2")

        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="SecureEmail"
        )

        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM user_signup WHERE username=%s AND password=%s",
            (uname, pwd)
        )
        result = cur.fetchone()

        if result:
            username = uname
            return render(request, "UserScreen.html", {"data": "Welcome " + username})
        else:
            return render(request, "UserLogin.html", {"data": "Invalid Login"})


def ComposeMail(request):
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="SecureEmail"
    )
    cur = conn.cursor()
    cur.execute("SELECT username FROM user_signup")
    users = cur.fetchall()
    return render(request, "ComposeMail.html", {"users": users})


def ComposeMailAction(request):
    global username
    if request.method == "POST":
        receiver = request.POST.get("t1")
        subject = request.POST.get("t2")
        message = request.POST.get("t3")
        file = request.FILES["t4"]

        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="SecureEmail"
        )

        cur = conn.cursor()
        cur.execute("SELECT IFNULL(MAX(mail_id),0)+1 FROM emails")
        mail_id = cur.fetchone()[0]

        file_data = file.read()
        key = computeQuantumKeys(file_data)

        quantumEncryptMessage(
            message.encode(),
            key,
            "EmailApp/static/files/" + str(mail_id) + ".txt"
        )

        quantumEncryptMessage(
            file_data,
            key,
            "EmailApp/static/files/" + file.name
        )

        cur.execute(
            "INSERT INTO emails VALUES (%s,%s,%s,%s,%s,%s)",
            (mail_id, username, receiver, today, subject, file.name)
        )
        conn.commit()

        return render(request, "UserScreen.html",
                      {"data": "Mail Sent & Encrypted Successfully"})


def ViewEmail(request):
    global username
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="SecureEmail"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM emails")
    mails = cur.fetchall()
    return render(request, "ViewMail.html",
                  {"mails": mails, "user": username})


def DecryptMessage(request):
    mail_id = request.GET.get("msgid")
    path = "EmailApp/static/files/" + str(mail_id) + ".txt"
    plain_text = quantumDecryptMessage(path)
    return render(request, "UserScreen.html",
                  {"data": "Decrypted Message: " + plain_text.decode()})
