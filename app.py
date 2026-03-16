from django.shortcuts import render
import pymysql
from datetime import datetime
from django.http import HttpResponse
import os
import QuantumEncryption
from QuantumEncryption import *

username = ""

# -------------------- Compose Mail --------------------

def ComposeMailAction(request):
    global username
    if request.method == 'POST':
        receiver = request.POST.get('t1')
        subject = request.POST.get('t2')
        msg = request.POST.get('t3')
        today = str(datetime.now())

        file = request.FILES['t4']
        filename = file.name
        myfile = file.read()

        count = 0

        mysqlConnect = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='root',
            database='SecureEmail',
            charset='utf8'
        )

        with mysqlConnect:
            result = mysqlConnect.cursor()
            result.execute("select max(mail_id) from emails")
            lists = result.fetchall()

            for ls in lists:
                count = ls[0]

            if count is not None:
                count += 1
            else:
                count = 1

        # Encryption
        key = computeQuantumKeys(myfile)

        iv, ciphertext = quantumEncryptMessage(
            msg.encode(),
            key,
            "EmailApp/static/files/" + str(count) + ".txt"
        )

        iv, ciphertext = quantumEncryptMessage(
            myfile,
            key,
            "EmailApp/static/files/" + filename
        )

        dbconnection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='root',
            database='SecureEmail',
            charset='utf8'
        )

        dbcursor = dbconnection.cursor()

        qry = """INSERT INTO emails(mail_id,sender_name,receiver_name,send_date,subject,attached_file)
                 VALUES(%s,%s,%s,%s,%s,%s)"""

        dbcursor.execute(qry, (count, username, receiver, today, subject, filename))
        dbconnection.commit()

        context = {
            'data': 'Message successfully sent to ' + receiver +
                    ' Encrypted Message: ' + str(ciphertext)
        }

        return render(request, 'UserScreen.html', context)


# -------------------- Get Encrypted Preview --------------------

def getEncrypted(path):
    with open(path, "rb") as file:
        data = file.read()
    return data[0:10]


# -------------------- Decrypt Message --------------------

def DecryptMessage(request):
    if request.method == 'GET':
        msgid = request.GET.get('msgid')

        plain_text = quantumDecryptMessage(
            "EmailApp/static/files/" + msgid + ".txt"
        )

        context = {
            "data": "Decrypted Message: " + plain_text.decode()
        }

       