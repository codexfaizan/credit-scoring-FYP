from flask import Flask,render_template,request,request,jsonify, redirect, url_for,session, Response
from prediction import prediction
from flask_mysqldb import MySQL
import pdfkit
import pymysql
from fpdf import FPDF

app = Flask(__name__)
#db = SQLAlchemy(app)
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['MYSQL_HOST'] = '134.255.227.70'
app.config['MYSQL_USER'] = 'hamza'
app.config['MYSQL_PASSWORD'] = 'hamza123'
app.config['MYSQL_DB'] = 'credit_scoring'

app.secret_key="superkey"
message = "null"

mysql = MySQL(app)
#app.config['SECRET_KEY'] = 'thisisasecretkey'

#class User(db.Model):
 #   mobilenumber = db.Column(db.Integer, primary_key=True, unique=True)
  #  fullname = db.Column(db.String(30), nullable=False)
   #pasword = db.Column(db.String(40), nullable=False)
   # gender = db.Column(db.String(8), nullable=False)
    #email= db.Column(db.string(40), nullable=False)

@app.route("/",methods=['GET','POST'])
def base():
    return redirect("/login")

@app.route("/login",methods=['GET','POST'])
def login():
    msg=''
    if (request.method=='POST'):
        email=request.form['email']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute(f'SELECT * FROM info_table WHERE email="{email}" AND password="{password}"')
        record=cursor.fetchone()
        if record:
            session['loggedin']=True
            session['email']=record[4]
            session['password']=record[3]
            return redirect("/home")
        else:
            msg="The entered password or email is incorrect"
    return render_template('login.html')

@app.route("/signup",methods=['GET','POST'])
def signup():
    if (request.method=='POST'):
        name=request.form['fullname']
        username=request.form['username']
        password=request.form['password']
        mobilenumber=request.form['mobile']
        email=request.form['email']
        cursor=mysql.connection.cursor()
        cursor.execute(''' INSERT INTO info_table VALUES(%s,%s,%s,%s,%s)''',
        (name,username,password,email,mobilenumber))   
        mysql.connection.commit()
        cursor.close()
        print("I reached")
        return redirect("/login")
    return render_template('signup.html')

@app.route("/home")
def home():
    if (request.method=='POST'):
        print("Home was posted")
    return render_template('home.html')

@app.route("/about")
def hproducts():
    return render_template('about.html')

@app.route('/download/report/pdf')
def download_report():
    conn = None
    cursor = None
    try:
        #conn = mysql.connect()
        cursor=mysql.connection.cursor()
        #cursor = conn.cursor(pymysql.cursors.DictCursor)
         
        cursor.execute("SELECT * FROM home")
        result = cursor.fetchall()
 
        pdf = FPDF()
        pdf.add_page()
         
        page_width = pdf.w - 2 * pdf.l_margin
         
        pdf.set_font('Times','B',14.0) 
        pdf.cell(page_width, 0.0, 'Loan Data', align='C')
        pdf.ln(10)
 
        pdf.set_font('Courier', '', 12)
         
        col_width = page_width/7

        headers = ["Dependents", "Age", "Income", "Unsecured", "Debt %", "Days Late", "State Loans"]
         
        pdf.ln(1)
         
        th = pdf.font_size
        row = result[-1]
        #table headers
        for index, header in enumerate(headers):
            max_width = max(pdf.get_string_width(header), pdf.get_string_width(str(row[index])))+3
            pdf.cell(max_width, th, header, border=1)
        pdf.ln(th)
        for index, header in enumerate(headers):
            max_width = max(pdf.get_string_width(header), pdf.get_string_width(str(row[index])))+3
            pdf.cell(max_width, th, str(row[index]), border=1)
         
        pdf.ln(10)

        pdf.set_font('Times','B',14.0) 
        pdf.cell(page_width, 0.0, str(row[-1]), align='C')
        pdf.ln(10)
         
        pdf.set_font('Times','',10.0) 
        pdf.cell(page_width, 0.0, '- end of report -', align='C')
        print("Reached")
        cursor.close()
        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=employee_report.pdf'})
    except Exception as e:
        print(f"Error: {e}")
        cursor.close()
        return redirect("/home")


@app.route('/after-submit', methods=['POST', 'GET'])
def make_prediction():
    if request.method == 'POST':
        dependents=request.form['dependents']
        age=request.form['age']
        income=request.form['income']
        unsecured_lines=request.form['unsecured_lines']
        debt_ratio=request.form['debt_ratio']
        days_late=request.form['days_late']
        real_estate_loans=request.form['Real_Estate_Loans']

        input = [unsecured_lines, debt_ratio, days_late, real_estate_loans]
        global message 
        message = prediction(input)

        cursor=mysql.connection.cursor()
        cursor.execute(''' INSERT INTO home VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',
        (dependents,age,income,unsecured_lines,debt_ratio,days_late,real_estate_loans, message))   
        mysql.connection.commit()
        cursor.close()

        #update query (message value)

        # message ="hello"
        return render_template('after.html',message=message)
    else:
        return redirect('/home')

if __name__== "__main__":
    app.run(debug=True)