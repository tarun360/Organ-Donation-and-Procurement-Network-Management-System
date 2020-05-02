from flask import Flask,render_template,session,request,redirect,url_for,flash
import mysql.connector,hashlib
import matplotlib.pyplot as plt
import numpy as np

mydb = mysql.connector.connect(
  host='localhost',
  user='root',
  password='your_password',
  database = 'DBMS_PROJECT'
)
mycursor = mydb.cursor(buffered=True)

app = Flask(__name__)

@app.route("/",methods = ['POST', 'GET'])
@app.route("/home",methods = ['POST','GET'])
def home():
    if not session.get('login'):
        return render_template('login.html'),401
    else:
        if session.get('isAdmin') :
            return render_template('home.html',username=session.get('username'))
        else :
            return home_student()

@app.route("/login",methods = ['GET','POST'])
def login():
    if request.method=='POST' :
        query = """SELECT * FROM login WHERE username = '%s'""" %(request.form['username'])
        mycursor.execute(query)
        res = mycursor.fetchall()
        if mycursor.rowcount == 0:
            return home()
        if request.form['password'] != res[0][1]:
            return render_template('login.html')
        else:
            session['login'] = True
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            session['isAdmin'] = (request.form['username']=='admin')
            return home()
    return render_template('login.html')

@app.route("/show_update_detail",methods=['POST','GET'])
def show_update_detail():
    if not session.get('login'):
        return redirect( url_for('home') )
    if request.method=='POST':
        if request.form['User_ID'] =='':
            return render_template("search_detail.html")
        qry = "Select * from User where User.User_ID = %s" %(request.form['User_ID'])
        qry1 = "Select * from User_phone_no where User_ID = %s" %(request.form['User_ID'])
        mycursor.execute(qry)
        not_found=False
        res=()
        if(mycursor.rowcount > 0):
            res = mycursor.fetchone()
        else:
            not_found=True
        fields = mycursor.column_names
        qry_upd = "Select * from User where User_ID = %s" %(request.form['User_ID'])
        mycursor.execute(qry_upd)
        upd_res = ()
        if(mycursor.rowcount > 0):
            upd_res = mycursor.fetchone()
        fields_upd = mycursor.column_names
        mycursor.execute(qry1)
        phone_no = mycursor.fetchall()
        qry_pat = "select Patient_ID, organ_req, reason_of_procurement, Doctor_name from Patient inner join Doctor on Doctor.Doctor_ID = Patient.Doctor_ID and User_ID = %s" %(request.form['User_ID'])
        qry_don = "select Donor_ID, organ_donated, reason_of_donation, Organization_name from Donor inner join Organization on Organization.Organization_ID = Donor.Organization_ID and User_ID = %s" %(request.form['User_ID'])
        qry_trans = "select distinct Transaction.Patient_ID, Transaction.Donor_ID, Organ_ID, Date_of_transaction, Status from Transaction, Patient, Donor where (Patient.User_ID = %s and Patient.Patient_ID = Transaction.Patient_ID) or (Donor.User_Id= %s and Donor.Donor_ID = Transaction.Donor_ID)" %((request.form['User_ID']),(request.form['User_ID']))
        #
        res_pat = ()
        res_dnr = ()
        res_trans = ()
        mycursor.execute(qry_pat)
        if(mycursor.rowcount > 0):
            res_pat = mycursor.fetchall()
        fields_pat = mycursor.column_names
        #
        mycursor.execute(qry_don)
        if(mycursor.rowcount > 0):
            res_dnr = mycursor.fetchall()
        fields_dnr = mycursor.column_names
        #
        mycursor.execute(qry_trans)
        if(mycursor.rowcount > 0):
            res_trans = mycursor.fetchall()
        fields_trans = mycursor.column_names
        print(res_trans)
        if("show" in request.form):
            return render_template('show_detail_2.html',res = res,fields = fields, not_found=not_found, phone_no = phone_no, res_dnr = res_dnr, res_pat = res_pat,res_trans = res_trans,fields_trans = fields_trans, fields_dnr = fields_dnr, fields_pat = fields_pat)
        if("update" in request.form):
            return render_template('update_detail.html',res = upd_res,fields = fields_upd, not_found=not_found)
        if "delete" in request.form:
            if not_found:
                return render_template('show_detail_2.html',res = res,fields = fields, not_found=not_found, phone_no = phone_no,  res_dnr = res_dnr, res_pat = res_pat,res_trans = res_trans,fields_trans = fields_trans, fields_dnr = fields_dnr, fields_pat = fields_pat)
            else:
                qry2 = "DELETE FROM User where User_ID = %s" %(request.form['User_ID'])
                mycursor.execute(qry2)
                mydb.commit()
                return render_template("home.html")

@app.route("/search_detail",methods = ['POST','GET'])
def search_detail():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('search_detail.html')

#--------------Adding Information----------------------------

@app.route("/add_<id>_page",methods = ['POST','GET'])
def add_page(id):
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from " + id.capitalize()
    mycursor.execute(qry)
    fields = mycursor.column_names

    return render_template('add_page.html',success=request.args.get('success'), error=request.args.get('error'), fields = fields, id= id)

@app.route("/add_User", methods=['POST','GET'])
def add_User():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from User"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['User_ID','Medical_insurance'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    qry = "INSERT INTO User Values (%s,%s,%s,%s,%s,%s,%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='User', error=error,success=success))

@app.route("/add_User_phone_no", methods=['POST','GET'])
def add_User_phone_no():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from User_phone_no"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['User_ID','Phone_no'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    qry = "INSERT INTO User_phone_no Values (%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='User_phone_no', error=error,success=success))

@app.route("/add_Patient", methods=['POST','GET'])
def add_Patient():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Patient"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['Patient_ID','User_ID','Doctor_ID'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    qry = "INSERT INTO Patient Values (%s,%s,%s,%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='Patient', error=error,success=success))

@app.route("/add_Donor", methods=['POST','GET'])
def add_Donor():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Donor"
    mycursor.execute(qry)
    fields = mycursor.column_names
    val = ()
    for field in fields:
        temp = request.form.get(field)
        if field not in ['Donor_ID','User_ID','Organization_ID'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)
    mycursor.execute( "START TRANSACTION;" )
    qry = "INSERT INTO Donor Values (%s,%s,%s,%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False

    qry_insert = "insert into Organ_available (Organ_name, Donor_ID) Values (%s,%s) "%(val[1],val[0])

    mycursor.execute(qry_insert)

    mycursor.execute("COMMIT;")

    mydb.commit()

    return redirect(url_for('add_page', id='Donor', error=error,success=success))

@app.route("/add_Doctor", methods=['POST','GET'])
def add_Doctor():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Doctor"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['Doctor_ID','Organization_ID'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    qry = "INSERT INTO Doctor Values (%s,%s,%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='Doctor', error=error,success=success))

@app.route("/add_Doctor_phone_no", methods=['POST','GET'])
def add_Doctor_phone_no():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Doctor_phone_no"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['Doctor_ID','Phone_no'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    qry = "INSERT INTO Doctor_phone_no Values (%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='Doctor_phone_no', error=error,success=success))

@app.route("/add_Organ_available", methods=['POST','GET'])
def add_Organ_available():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Organ_available"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['Organ_ID','Donor_ID'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    qry = "INSERT INTO Organ_available Values (%s,%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='Organ_available', error=error,success=success))


@app.route("/add_Organization", methods=['POST','GET'])
def add_Organization():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Organization"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['Government_approved','Organization_ID'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    qry = "INSERT INTO Organization Values (%s,%s,%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='Organization', error=error,success=success))

@app.route("/add_Organization_phone_no", methods=['POST','GET'])
def add_Organization_phone_no():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Organization_phone_no"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['Organization_ID','Phone_no'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    qry = "INSERT INTO Organization_phone_no Values (%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='Organization_phone_no', error=error,success=success))

@app.route("/add_Organization_head", methods=['POST','GET'])
def add_Organization_head():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Organization_head"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['Employee_ID','Term_length','Organization_ID'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    qry = "INSERT INTO Organization_head Values (%s,%s,%s,%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False
    mydb.commit()

    return redirect(url_for('add_page', id='Organization_head', error=error,success=success))

@app.route("/add_Transaction", methods=['POST','GET'])
def add_Transaction_head():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Transaction"
    mycursor.execute(qry)
    fields = mycursor.column_names

    val = ()

    for field in fields:
        temp = request.form.get(field)
        if field not in ['Patient_ID','Donor_ID','Status','Organ_ID'] and temp != '':
            temp = "\'"+temp+"\'"
        if temp == '':
            temp = 'NULL'
        val = val + (temp,)

    mycursor.execute( "START TRANSACTION;" )
    qry = "INSERT INTO Transaction Values (%s,%s,%s,%s,%s)"%val
    print(qry)
    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error : User not Inserted")
        error = True
        success = False

    qry_insert = "delete from Organ_available where Organ_ID = %s "%val[1]

    mycursor.execute(qry_insert)

    mycursor.execute("COMMIT;")

    mydb.commit()

    return redirect(url_for('add_page', id='Transaction', error=error,success=success))

#------------------------Update details-------------------------------------		#-------------------------------------------------------------

@app.route("/update_user_page",methods = ['POST','GET'])
def update_user_page():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry_upd = "Select * from User"
    mycursor.execute(qry_upd)
    fields_upd = mycursor.column_names
    upd_res=[None]*len(fields_upd)
    return render_template('update_user_page.html',fields = fields_upd,res = upd_res)

@app.route("/update_user_details",methods = ['GET','POST'])
def update_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    mycursor.execute("SELECT * from User")
    fields = mycursor.column_names
    qry = "UPDATE User SET "
    for field in fields:
        if request.form[field] not in ['None','']:
            if field in ['User_ID','Medical_insurance']:
                qry = qry + "%s = %s , " %(field,request.form[field])
            else:
                qry = qry + " %s = \'%s\' , " %(field,request.form[field])
        else:
            qry = qry + "%s = NULL , " %(field)
    qry = qry[:-2]
    qry = qry + "WHERE User_ID = %s;" %(request.form['User_ID'])
    print(qry)
    try:
        mycursor.execute(qry)
    except:
        print("update error")
    mydb.commit()
    qry2 = "select * from User where User_ID = %s" %(request.form['User_ID'])
    mycursor.execute(qry2)
    res = mycursor.fetchone()
    qry = "Select * from User where User.User_ID = %s" %(request.form['User_ID'])
    qry1 = "Select * from User_phone_no where User_ID = %s" %(request.form['User_ID'])
    mycursor.execute(qry)
    not_found=False
    res=()
    if(mycursor.rowcount > 0):
        res = mycursor.fetchone()
    else:
        not_found=True
    fields = mycursor.column_names
    qry_upd = "Select * from User where User_ID = %s" %(request.form['User_ID'])
    mycursor.execute(qry_upd)
    upd_res = ()
    if(mycursor.rowcount > 0):
        upd_res = mycursor.fetchone()
    fields_upd = mycursor.column_names
    mycursor.execute(qry1)
    phone_no = mycursor.fetchall()
    qry_pat = "select Patient_ID, organ_req, reason_of_procurement, Doctor_name from Patient inner join Doctor on Doctor.Doctor_ID = Patient.Doctor_ID and User_ID = %s" %(request.form['User_ID'])
    qry_don = "select Donor_ID, organ_donated, reason_of_donation, Organization_name from Donor inner join Organization on Organization.Organization_ID = Donor.Organization_ID and User_ID = %s" %(request.form['User_ID'])
    qry_trans = "select distinct Transaction.Patient_ID, Transaction.Donor_ID, Organ_ID, Date_of_transaction, Status from Transaction, Patient, Donor where (Patient.User_ID = %s and Patient.Patient_ID = Transaction.Patient_ID) or (Donor.User_Id= %s and Donor.Donor_ID = Transaction.Donor_ID)" %((request.form['User_ID']),(request.form['User_ID']))
    #
    res_pat = ()
    res_dnr = ()
    res_trans = ()
    mycursor.execute(qry_pat)
    if(mycursor.rowcount > 0):
        res_pat = mycursor.fetchall()
    fields_pat = mycursor.column_names
    #
    mycursor.execute(qry_don)
    if(mycursor.rowcount > 0):
        res_dnr = mycursor.fetchall()
    fields_dnr = mycursor.column_names
    #
    mycursor.execute(qry_trans)
    if(mycursor.rowcount > 0):
        res_trans = mycursor.fetchall()
    fields_trans = mycursor.column_names
    # if("show" in request.form):
    return render_template('show_detail_2.html',res = res,fields = fields, not_found=not_found, phone_no = phone_no, res_dnr = res_dnr, res_pat = res_pat,res_trans = res_trans,fields_trans = fields_trans, fields_dnr = fields_dnr, fields_pat = fields_pat)
    # return render_template("show_detail.html",res = res,fields=fields,not_found = False)

@app.route("/update_patient_page",methods = ['POST','GET'])
def update_patient_page():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry_upd = "Select * from Patient"
    mycursor.execute(qry_upd)
    fields_upd = mycursor.column_names
    upd_res=[None]*len(fields_upd)
    return render_template('update_patient_page.html',fields = fields_upd,res = upd_res)

@app.route("/update_patient_details",methods = ['GET','POST'])
def update_patient_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    mycursor.execute("SELECT * from Patient")
    fields = mycursor.column_names
    qry = "UPDATE Patient SET "
    for field in fields:
        if request.form[field] not in ['None','']:
            if field in ['User_ID','Doctor_ID','Patient_ID']:
                qry = qry + "%s = %s , " %(field,request.form[field])
            else:
                qry = qry + " %s = \'%s\' , " %(field,request.form[field])
        else:
            qry = qry + "%s = NULL , " %(field)
    qry = qry[:-2]
    qry = qry + "WHERE Patient_ID = %s and organ_req = \'%s\';" %(request.form['Patient_ID'],request.form['organ_req'])
    print(qry)
    try:
        mycursor.execute(qry)
    except:
        print("update error")
    mydb.commit()
    qry2 = "select * from Patient WHERE Patient_ID = %s and organ_req = \'%s\';" %(request.form['Patient_ID'],request.form['organ_req'])
    mycursor.execute(qry2)
    res = mycursor.fetchone()
    print(res)
    print(qry2)
    return render_template("show_detail.html",res = res,fields=fields,not_found = False)

@app.route("/update_donor_page",methods = ['POST','GET'])
def update_donor_page():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry_upd = "Select * from Donor"
    mycursor.execute(qry_upd)
    fields_upd = mycursor.column_names
    upd_res=[None]*len(fields_upd)
    return render_template('update_donor_page.html',fields = fields_upd,res = upd_res)

@app.route("/update_donor_details",methods = ['GET','POST'])
def update_donor_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    mycursor.execute("SELECT * from Donor")
    fields = mycursor.column_names
    qry = "UPDATE Donor SET "
    for field in fields:
        if request.form[field] not in ['None','']:
            if field in ['User_ID','Organization_ID','Donor_ID']:
                qry = qry + "%s = %s , " %(field,request.form[field])
            else:
                qry = qry + " %s = \'%s\' , " %(field,request.form[field])
        else:
            qry = qry + "%s = NULL , " %(field)
    qry = qry[:-2]
    qry = qry + "WHERE Donor_ID = %s and organ_donated = \"%s\";" %(request.form['Donor_ID'],request.form['organ_donated'])
    print(qry)
    try:
        mycursor.execute(qry)
    except:
        print("update error")
    mydb.commit()
    qry2 = "select * from Patient WHERE Donor_ID = %s and organ_donated = \"%s\";" %(request.form['Donor_ID'],request.form['organ_donated'])
    mycursor.execute(qry2)
    res = mycursor.fetchone()
    print(res)
    print(qry2)
    return render_template("show_detail.html",res = res,fields=fields,not_found = False)

@app.route("/update_doctor_page",methods = ['POST','GET'])
def update_doctor_page():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry_upd = "Select * from Doctor"
    mycursor.execute(qry_upd)
    fields_upd = mycursor.column_names
    upd_res=[None]*len(fields_upd)
    return render_template('update_doctor_page.html',fields = fields_upd,res = upd_res)

@app.route("/update_doctor_details",methods = ['GET','POST'])
def update_doctor_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    mycursor.execute("SELECT * from Doctor")
    fields = mycursor.column_names
    qry = "UPDATE Doctor SET "
    for field in fields:
        if request.form[field] not in ['None','']:
            if field in ['Doctor_ID','Organization_ID']:
                qry = qry + "%s = %s , " %(field,request.form[field])
            else:
                qry = qry + " %s = \'%s\' , " %(field,request.form[field])
        else:
            qry = qry + "%s = NULL , " %(field)
    qry = qry[:-2]
    qry = qry + "WHERE Doctor_ID = %s;" %(request.form['Doctor_ID'])
    print(qry)
    try:
        mycursor.execute(qry)
    except:
        print("update error")
        return render_template('error_page.html')
    mydb.commit()
    qry2 = "select * from Doctor WHERE Doctor_ID = %s;" %(request.form['Doctor_ID'])
    mycursor.execute(qry2)
    res = mycursor.fetchone()
    return render_template("show_detail.html",res = res,fields=fields,not_found = False)

@app.route("/update_organization_page",methods = ['POST','GET'])
def update_organization_page():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry_upd = "Select * from Organization"
    mycursor.execute(qry_upd)
    fields_upd = mycursor.column_names
    upd_res=[None]*len(fields_upd)
    return render_template('update_organization_page.html',fields = fields_upd,res = upd_res)

@app.route("/update_organization_details",methods = ['GET','POST'])
def update_organization_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    mycursor.execute("SELECT * from Organization")
    fields = mycursor.column_names
    qry = "UPDATE Organization SET "
    for field in fields:
        if request.form[field] not in ['None','']:
            if field in ['Organization_ID','Government_approved']:
                qry = qry + "%s = %s , " %(field,request.form[field])
            else:
                qry = qry + " %s = \'%s\' , " %(field,request.form[field])
        else:
            qry = qry + "%s = NULL , " %(field)
    qry = qry[:-2]
    qry = qry + "WHERE Organization_ID = %s;" %(request.form['Organization_ID'])
    print(qry)
    try:
        mycursor.execute(qry)
    except:
        print("update error")
        return render_template('error_page.html')
    mydb.commit()
    qry2 = "select * from Organization WHERE Organization_ID = %s;" %(request.form['Organization_ID'])
    mycursor.execute(qry2)
    res = mycursor.fetchone()
    return render_template("show_detail.html",res = res,fields=fields,not_found = False)
# @app.route("/update_organization_head_page",methods = ['POST','GET'])
# def update_organization_head_page():
#     if not session.get('login'):
#         return redirect( url_for('home') )
#     qry_upd = "Select * from Organization_head"
#     mycursor.execute(qry_upd)
#     fields_upd = mycursor.column_names
#     upd_res=[None]*len(fields_upd)
#     return render_template('update_organization_head_page.html',fields = fields_upd,res = upd_res)
# @app.route("/update_organization_head_details",methods = ['GET','POST'])
# def update_organization_head_details():
#     if not session.get('login'):
#         return redirect( url_for('home') )
#     mycursor.execute("SELECT * from Organization_head")
#     fields = mycursor.column_names
#     qry = "UPDATE Organization_head SET "
#     for field in fields:
#         if request.form[field] not in ['None','']:
#             if field in ['Organization_ID','Employee_ID','Term_length']:
#                 qry = qry + "%s = %s , " %(field,request.form[field])
#             else:
#                 qry = qry + " %s = \'%s\' , " %(field,request.form[field])
#         else:
#             qry = qry + "%s = NULL , " %(field)
#     qry = qry[:-2]
#     qry = qry + "WHERE Organization_ID = %s and Employee_ID = %s;" %(request.form['Organization_ID'],request.form['Employee_ID'])
#     print(qry)
#     try:
#         mycursor.execute(qry)
#     except:
#         return render_template('error_page.html',qry=qry)
#     mydb.commit()
#     qry2 = "select * from Organization WHERE Organization_ID = %s and Employee_ID = %s;" %(request.form['Organization_ID'],request.form['Employee_ID'])
#     mycursor.execute(qry2)
#     res = mycursor.fetchone()
#     return render_template("show_detail.html",res = res,fields=fields,not_found = False)

#----------------------------Logout-----------------------------------------
@app.route("/logout", methods=['POST','GET'])
def logout():
    session['login'] = False
    session['isAdmin'] = False
    return redirect("/login")

#-----------------------Searching Information------------------------------

@app.route("/search_User_details",methods=['GET','POST'])
def search_User_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from User"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_Patient_details",methods=['GET','POST'])
def search_Patient_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Patient"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_Donor_details",methods=['GET','POST'])
def search_Donor_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Donor"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_Organ_details",methods=['GET','POST'])
def search_Organ_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Organ_available"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_Organization_details",methods=['GET','POST'])
def search_Organization_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Organization"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_Organization_head_details",methods=['GET','POST'])
def search_Organization_head_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Organization_head"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_Doctor_details",methods=['GET','POST'])
def search_Doctor_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Doctor"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()

    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_Transaction",methods=['GET','POST'])
def search_Transaction_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from Transaction"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()
    return render_template('/search_and_show_list.html',res=res,fields=fields)

@app.route("/search_log",methods=['GET','POST'])
def search_log_details():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "SELECT * from log"
    mycursor.execute(qry)
    fields = mycursor.column_names
    res = mycursor.fetchall()
    return render_template('/search_and_show_list.html',res=res,fields=fields)

#---------------------Remove Pages--------------------------------------

@app.route('/remove_user',methods=['GET','POST'])
def remove_user():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_user.html')

@app.route('/remove_patient',methods=['GET','POST'])
def remove_hostel():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_patient.html')

@app.route('/remove_donor',methods=['GET','POST'])
def remove_room():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_donor.html')

@app.route('/remove_doctor',methods=['GET','POST'])
def remove_doctor():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_doctor.html')

@app.route('/remove_organization',methods=['GET','POST'])
def remove_organization():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_organization.html')

@app.route('/remove_organization_head',methods=['GET','POST'])
def remove_organization_head():
    if not session.get('login'):
        return redirect( url_for('home') )
    return render_template('/remove_organization_head.html')


#----------------Actual Deletion from database------------------------

@app.route('/del_user',methods=['GET','POST'])
def del_hostel():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "delete from User where User_ID="+str(request.form['User_ID'])
    print(qry)
    try:
        mycursor.execute(qry)
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )

@app.route('/del_patient',methods=['GET','POST'])
def del_patient():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "delete from Patient where Patient_ID="+str(request.form['Patient_ID'])+" and organ_req=\'%s\'"%(request.form['organ_req'])
    print(qry)
    try:
        mycursor.execute(qry)
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )

@app.route('/del_donor',methods=['GET','POST'])
def del_donor():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "delete from Donor where Donor_ID="+str(request.form['Donor_ID'])+" and organ_donated=\'%s\'" %request.form['organ_donated']
    try:
        mycursor.execute(qry)
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )


@app.route('/del_doctor',methods=['GET','POST'])
def del_doctor():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "delete from Doctor where Doctor_ID="+str(request.form['Doctor_ID'])
    try:
        mycursor.execute(qry)
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )


@app.route('/del_organization',methods=['GET','POST'])
def del_organization():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "delete from Organization where Organization_ID="+str(request.form['Organization_ID'])
    try:
        mycursor.execute(qry)
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )


@app.route('/del_organization_head',methods=['GET','POST'])
def del_organization_head():
    if not session.get('login'):
        return redirect( url_for('home') )
    qry = "delete from Organization_head where Organization_ID="+str(request.form['Organization_ID'])+" and Employee_ID="+str(request.form['Employee_ID'])
    try:
        mycursor.execute(qry)
    except:
        print("Error in deletion")
    mydb.commit()
    return redirect( url_for('home') )
#------------------------------------------------------------------------

@app.route('/contact_admin_page',methods=['GET','POST'])
def contact_admin_page():
    print(session.get('isAdmin'))
    if not session.get('login') or session.get('isAdmin'):
        return redirect( url_for('home') )
    return render_template('contact_admin_page.html')

@app.route('/contact_admin',methods=['GET','POST'])
def contact_admin():
    if not session.get('login') or session.get('isAdmin'):
        return redirect( url_for('home') )
    username = session.get('username')
    message = request.form['message']

    qry = "insert into Messages (username,message) values (\'"+username+"\',\'"+message+"\')"

    success = True
    error = False
    try:
        mycursor.execute(qry)
    except:
        print("Error")
        error = True
        success = False
    mydb.commit()

    return render_template('contact_admin_page.html',error=error,success=success)


@app.route('/see_messages',methods=['GET','POST'])
def see_messages():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect( url_for('home') )

    qry = "Select * from Messages"
    mycursor.execute(qry)
    msg = mycursor.fetchall()

    return render_template('see_messages.html',msg=msg)

@app.route('/seen_message',methods=['GET','POST'])
def seen_message():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect( url_for('home') )

    print(request.form['id'])

    msg_id = request.form['id']

    qry = "delete from Messages where message_id=\'"+msg_id+"\'"
    mycursor.execute(qry)
    mydb.commit()

    return redirect(url_for('see_messages'))

@app.route('/statistics', methods=['GET','POST'])
def stats():
    if not session.get('login') or not session.get('isAdmin'):
        return redirect( url_for('home') )
    qry = "select organ_donated, count(Donor_ID) from Donor group by organ_donated"
    mycursor.execute(qry)
    stats_donor = mycursor.fetchall()
    A = []
    B = []
    for organ in stats_donor:
        A.append(organ[0])
        B.append(organ[1])
    plt.pie(B, labels = A)
    plt.savefig('./static/donor_stat.png')
    # plt.show()
    plt.close()
    A.clear()
    B.clear()
    qry = "select organ_req, count(Patient_Id) from Patient group by organ_req"
    mycursor.execute(qry)
    stats_patient = mycursor.fetchall()
    A = []
    B = []
    for Patient in stats_patient:
        A.append(Patient[0])
        B.append(Patient[1])
    plt.pie(B, labels = A)
    plt.savefig('./static/Patient_stat.jpeg')
    # plt.show()
    plt.close()
    qry = "select distinct Organ_donated from Transaction inner join Donor on Transaction.Donor_ID = Donor.Donor_ID"
    mycursor.execute(qry)
    list = mycursor.fetchall()
    organ_list = []
    for organ in list:
        print(organ)
        organ_list.append(organ[0])
    print(organ)
    A.clear()
    B.clear()
    for organ in organ_list:
        qry = "select count(*) from Transaction inner join Donor on Donor.Donor_ID = Transaction.Donor_ID where Organ_donated = '%s' and Status = 1" %organ
        print(qry)
        mycursor.execute(qry)
        a = mycursor.fetchone()
        A.append(a[0])
        qry = "select count(*) from Transaction inner join Donor on Donor.Donor_ID = Transaction.Donor_ID where Organ_donated = '%s' and Status = 0" %organ
        print(qry)
        mycursor.execute(qry)
        b = mycursor.fetchone()
        B.append(b[0])
    print(A)
    print(B)
    print(organ_list)
    N = len(organ_list)
    fig, ax = plt.subplots()
    ind = np.arange(N)
    width = 0.05
    plt.bar(ind, A, width, label='SUCCESS')
    plt.bar(ind + width, B, width,label='FAILURE')
    plt.ylabel('Number of transplantation')
    plt.xlabel('Organ')
    plt.title('SUCCESS V/S FAILURE IN ORGAN TRANSPLANTATION')
    plt.xticks(ind + width / 2, organ_list)
    plt.legend(loc='best')
    plt.savefig('./static/success.jpeg')
    return render_template('statistics.html')

if __name__ == "__main__":
    app.secret_key = 'sec key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
