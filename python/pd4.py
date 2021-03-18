from flask import Flask, render_template, url_for, request, redirect, flash, session, redirect
import csv
import mysql.connector as mysqlconnector
from mysql.connector import errorcode
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Template_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=Template_dir,
            static_folder=static_dir)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

cnx = None

config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'debate',
    'raise_on_warnings': True
}

try:

    cnx = mysqlconnector.connect(**config)
    print('CONNECTED')
except mysqlconnector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cnx.close()


@app.route('/')
def Index():
    cnx = mysqlconnector.connect(
        user='root', password='', host='localhost', database='debate')
    cursor = cnx.cursor()
    query = "SELECT `topic_name`, `uemail`, `topic_id` FROM `topic` "
    cursor.execute(query)
    data = cursor.fetchall()

    topiclist = data[0]

    topicname = topiclist[0]
    uemail = topiclist[1]
    topicid = topiclist[2]

    print(data)
    topiclist = data[0]
    topicname = topiclist[0]
    uemail = topiclist[1]
    topicid = topiclist[2]
    print(topicid)

    return render_template('Main.html', topiclist=data, id=topicid)


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        flash("Already logged in")
        return redirect(url_for('Index'))
    else:
        if request.method == "POST":

            uname = request.form['email']
            passw = request.form['pwd']
            print(uname)
            print(passw)

            cnx = mysqlconnector.connect(
                user='root', password='', host='localhost', database='debate')
            cursor = cnx.cursor()

            query = ("SELECT * FROM user WHERE email = " +
                     "'" + str(uname) + "'")

            cursor.execute(query, (uname))

            userdatalist = cursor.fetchall()
            if (userdatalist):
                usertuple = userdatalist[0]
                if (usertuple):
                    if uname == usertuple[1] and passw == usertuple[2]:
                        session['loggedin'] = True

                        session['useremail'] = uname
                        session['username'] = usertuple[0]



                        return redirect(url_for('Index'))
                    else:
                        flash("email and passowrd doesn't matched")
                else:
                    flash('No user found for this email')
                    print('No data found')
            else:
                print('No data found')
                flash('No user found for this email')

        return render_template('login.html')


# REGISTERATION
@app.route('/Registration', methods=['GET', 'POST'])
def Registration():
    if 'loggedin' in session:
        flash("Already logged in")
        return redirect(url_for('Index'))
    else:
        if request.method == "POST":

            uemail = request.form['regemail']
            uname = request.form['regname']
            passw = request.form['regpass']
            cpassw = request.form['cregpass']
            print(uemail)
            print(passw)
            print(cpassw)
            print(uname)

            if passw == cpassw:
                cnx = mysqlconnector.connect(
                    user='root', password='', host='localhost', database='debate')
                cursor = cnx.cursor()
                query = ("SELECT * FROM user WHERE email = " +
                         "'" + str(uemail) + "'")
                cursor.execute(query, (uemail))
                userdatalist = cursor.fetchall()
                if (userdatalist):
                    flash("User of this email already exist try with different email")
                    return render_template('Registration.html')
                else:

                    cnx = mysqlconnector.connect(
                        user='root', password='', host='localhost', database='debate')
                    cursor = cnx.cursor()
                    cursor.execute(
                        'INSERT INTO user VALUES (%s, %s, %s)', (uname, uemail, passw))

                    cnx = mysqlconnector.connect(
                        user='root', password='', host='localhost', database='debate')
                    cursor = cnx.cursor()
                    cursor.execute(
                        'INSERT INTO user VALUES (%s, %s, %s)', (uname, uemail, passw))

                    cnx.commit()
                    print("DONE")
                    session['loggedin'] = True
                    session['useremail'] = uemail
                    session['username'] = uname
                    flash('User reigstration successfull')
                    return redirect(url_for('Index'))
            else:
                flash("Please write the same password on both fields")

        return render_template('Registration.html')


def getmetopic(topicID):
    cnx = mysqlconnector.connect(
        user='root', password='', host='localhost', database='debate')
    cursor = cnx.cursor()
    query = ("SELECT * FROM topic WHERE topic_id = " + "'" + str(topicID) + "'")
    cursor.execute(query, (topicID))
    topicdatalist = cursor.fetchall()
    query = ("SELECT * FROM topicreplies WHERE topic_id = " +
             "'" + str(topicID) + "'")
    cursor.execute(query, (topicID))
    topicreplylist = cursor.fetchall()
    query = ("SELECT * FROM claim WHERE topic_id = " + "'" + str(topicID) + "'")
    cursor.execute(query, (topicID))
    claimlist = cursor.fetchall()
    print(topicdatalist)
    returnid1(topicID)
    print(topicID)
    print(topicreplylist)
    print("**CLAIM**" + str(claimlist))
    if (topicdatalist):
        topictuple = topicdatalist[0]
        return render_template('Topic.html', topicdata=topictuple, topicreply=topicreplylist, claimdata=claimlist)
    else:
        flash('No topic found')
        return redirect(url_for('Index'))


def returnid1(*x):
    global a
    for i in x:
        a = i
    return a


@app.route('/topic', methods=['GET', 'POST'])
def topic():
    if 'loggedin' in session:
        if request.method == "POST":
            topicID = request.form['topicid']

            return getmetopic(topicID)
        else:
            if 'topicid' in request.args:
                topicid = request.args['topicid']

                return getmetopic(topicid)
            flash('No topic found')
            return redirect(url_for('Index'))
    else:
        flash('Please Sign In to Continue')
        return render_template('login.html')


@app.route('/topicinsert', methods=['GET', 'POST'])
def topicinsert():
    if 'loggedin' in session:
        if request.method == "POST":
            currtime = datetime.now().strftime('%I:%M %p')
            uemail = session['useremail']
            uname = session['username']
            topicname = request.form['topicname']
            content = request.form['content']
            cnx = mysqlconnector.connect(
                user='root', password='', host='localhost', database='debate')
            cursor = cnx.cursor()
            cursor.execute(
                'INSERT INTO `topic`(`topic_id`, `uname`, `uemail`, `topic_name`, `topic_content`, `timestamp`) '
                'VALUES (NULL, %s, %s, %s, %s, %s)',
                (uname, uemail, topicname, content, currtime))

            cnx.commit()
            return redirect(url_for('Index'))
        else:
            return render_template('TopicInsert.html')
    else:
        flash('Please Sign In to Continue')
        return render_template('login.html')


@app.route('/topicrpeply', methods=['GET', 'POST'])
def topicrpeply():
    if request.method == "POST":
        uemail = session['useremail']
        topicreply = request.form['reply']
        choice = request.form.get('choice')
        topicid = request.form['topicid']
        currtime = datetime.now().strftime('%I:%M %p')
        print(choice)
        cnx = mysqlconnector.connect(
            user='root', password='', host='localhost', database='debate')
        cursor = cnx.cursor()
        cursor.execute(
            'INSERT INTO `topicreplies`(`tr_id`, `topic_id`, `uemail`, `reply`, `timestamp`, `topic_replytype`) VALUES (NULL , %s, %s, %s, %s, %s)',
            (topicid, uemail, topicreply, currtime, choice))
        cnx.commit()

        return redirect(url_for('topic', topicid=topicid))
    return redirect(url_for('Index'))


@app.route('/claiminsert', methods=['GET', 'POST'])
def claiminsert():
    if 'loggedin' in session:
        if request.method == "POST":

            currtime = datetime.now().strftime('%I:%M %p')
            tid = returnid1()
            uemail = session['useremail']
            title = request.form['title']
            content = request.form['content']
            claimtype = request.form['choice']
            cnx = mysqlconnector.connect(
                user='root', password='', host='localhost', database='debate')
            cursor = cnx.cursor()
            cursor.execute(
                'INSERT INTO `claim`(`claim_id`, `topic_id`, `uemail`, `timestamp`, `claim_title`, `content`, '
                '`claimtype`) VALUES '
                '(NULL,%s,%s,%s,%s,%s,%s)',
                (tid, uemail, currtime, title, content, claimtype))

            cnx.commit()
            return redirect(url_for('topic', topicid=tid))
        else:
            return render_template('ClaimInsert.html')
    else:
        flash('Please Sign In to Continue')
        return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


def getmeclaims(claimid, topicid):
    print(claimid)
    print(topicid)
    cnx = mysqlconnector.connect(
        user='root', password='', host='localhost', database='debate')
    cursor = cnx.cursor()
    query = ("SELECT * FROM claim WHERE claim_id = " + "'" + str(claimid) + "'")
    cursor.execute(query, (claimid))
    claimdatalist = cursor.fetchall()
    query = ("SELECT * FROM claimreply WHERE claim_id = " +
             "'" + str(claimid) + "'")
    cursor.execute(query, (claimid))
    claimreplylist = cursor.fetchall()
    query = ("SELECT topic_name FROM topic WHERE topic_id = " +
             "'" + str(topicid) + "'")
    cursor.execute(query, (topicid))
    topicnamedata = cursor.fetchall()
    topicnametuple = topicnamedata[0]
    print(claimreplylist)
    print(topicnamedata)
    if claimdatalist:
        claimdatatuple = claimdatalist[0]
        print(claimdatatuple)
        return render_template('claimview.html', claimdata=claimdatatuple, claimreply=claimreplylist,
                               topictitle=topicnametuple[0])
    else:
        flash('No topic found')
        return redirect(url_for('Index'))


@app.route('/claimview', methods=['GET', 'POST'])
def claimview():
    if 'loggedin' in session:
        if request.method == "POST":
            claimid = request.form["claimid"]
            topicid = request.form["topicid"]
            return getmeclaims(claimid, topicid)
        else:
            if 'topicid' and 'claimid' in request.args:
                topicid = request.args['topicid']
                claimid = request.args['claimid']
                return getmeclaims(claimid, topicid)
            flash('No claim found')
            return redirect(url_for('Index'))
    else:
        flash('Please Sign In to Continue')
        return render_template('login.html')


@app.route('/claimreply', methods=['GET', 'POST'])
def claimreply():
    if request.method == "POST":
        uemail = session['useremail']
        claimreply = request.form['reply']
        choice = request.form.get('choice')
        claimid = request.form['claimid']
        topicid = request.form['topicid']
        currtime = datetime.now().strftime('%I:%M %p')
        print(choice)
        cnx = mysqlconnector.connect(
            user='root', password='', host='localhost', database='debate')
        cursor = cnx.cursor()
        cursor.execute(
            'INSERT INTO `claimreply`(`claimreply_id`, `claim_id`, `uemail`, `reply`, `timestamp`, `claim_replytype`) VALUES (NULL , %s, %s, %s, %s, %s)',
            (claimid, uemail, claimreply, currtime, choice))
        cnx.commit()
        return redirect(url_for('claimview', claimid=claimid, topicid=topicid))
    return redirect(url_for('Index'))

# added search functionality.


@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        searchkeyword = request.form['search']
        cnx = mysqlconnector.connect(
            user='root', password='', host='localhost', database='debate')
        cursor = cnx.cursor()
        # param = '%b%'
        p = '%'+searchkeyword+'%'
        query = "SELECT `topic_name` FROM `topic` WHERE topic_name LIKE"+"'"+p+"'"
        cursor.execute(query)
        data = cursor.fetchall()
        # print(data)
        flash('These are the top search results we got for you!!!')
        errormessage = "OOOPS!!! We couldnt find any topics matching that search keyword, kindly try a different keyword"
    return render_template('searchresults.html', error=errormessage, datas=data)


@app.route('/content/view/', methods=['GET', 'POST'])
def viewcontents():
    if 'loggedin' in session:
        topicname = request.form['topicname']

        cnx = mysqlconnector.connect(
            user='root', password='', host='localhost', database='debate')
        cursor = cnx.cursor()
        # param = '%b%'

        query = "SELECT * FROM `topic` WHERE topic_name ="+"'"+topicname+"'"
        cursor.execute(query)
        data = cursor.fetchall()
        # print(data[0][1])
        topiccontent = data[0]
        topicID = data[0][1]

        # query = ("SELECT * FROM topic WHERE topic_id = " + "'" + str(topicID) + "'")
        # cursor.execute(query, (topicID))
        # topicdatalist = cursor.fetchall()
        query = ("SELECT * FROM topicreplies WHERE topic_id = " +
                 "'" + str(topicID) + "'")
        cursor.execute(query, (topicID))
        topicreplylist = cursor.fetchall()
        query = ("SELECT * FROM claim WHERE topic_id = " +
                 "'" + str(topicID) + "'")
        cursor.execute(query, (topicID))
        claimlist = cursor.fetchall()
        print(data[0][0])
        topiccontents = data[0]
        return render_template('viewcontent.html', topicdata=topiccontents,  topicreply=topicreplylist, claimdata=claimlist)
    else:
        flash('Please Sign In to Continue')
        return render_template('login.html')


# ("SELECT * FROM claimreply WHERE claim_id = " + "'" + str(claimid) + "'")


# if (topicdatalist):
#     topictuple = topicdatalist[0]
#     return render_template('Topic.html', topicdata=topictuple, topicreply=topicreplylist, claimdata=claimlist)


@app.route('/claimblog', methods=['GET', 'POST'])
def addblog():
    multiselect = request.form.getlist('checkbox')
    title = request.form['title']
    content = request.form['content']
    # initialize an empty string
    str1 = ""
    s = multiselect
    # traverse in the string
    for ele in s:
        str1 += ele

    # return string
    print(str1)
    currtime = datetime.now().strftime('%I:%M %p')

    uemail = session['useremail']

    cnx = mysqlconnector.connect(
        user='root', password='', host='localhost', database='debate')
    cursor = cnx.cursor()
    cursor.execute(
        'INSERT INTO `claim`(`claim_id`, `topic_id`, `uemail`, `timestamp`, `claim_title`, `content`, '
        '`claimtype`,`claimrelateid`) VALUES '
        '(NULL,NULL,%s,%s,%s,%s,NULL,%s)',
        (uemail, currtime, title, content, str1))

    cnx.commit()

    return render_template('claimrelation.html', uemail=uemail, currtime=currtime, title=title, content=content, str1=str1)


@app.route('/claimblogview', methods=['GET', 'POST'])
def blogview():
    if 'loggedin' in session:
        cnx = mysqlconnector.connect(
            user='root', password='', host='localhost', database='debate')
        cursor = cnx.cursor()
        query = ("SELECT * FROM claim ")
        cursor.execute(query)
        claims = cursor.fetchall()
        # print(claims)
        return render_template('claimblog.html', claimsdata=claims)
    else:
        flash('Please Sign In to Continue')
    return render_template('login.html')


@app.route('/topic/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    if  session['useremail'] == 'admin123@debate.com':
        cnx = mysqlconnector.connect(
            user='root', password='', host='localhost', database='debate')
        cursor = cnx.cursor()
        query = ("DELETE  FROM topic WHERE topic_id="+"'"+str(id)+"'")
        cursor.execute(query)
        cnx.commit()

        return redirect('/')
    else:
        flash('Please Sign In with an admin account to perform this action')
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
