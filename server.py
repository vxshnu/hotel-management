from flask import Flask,redirect,render_template,request,url_for,session
import mysql.connector
import base64 
from datetime import datetime

myconn = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="root"
)
db=myconn.cursor()
db.execute("USE hotel")

app=Flask(__name__)

app.secret_key = '1234567890'

reservationid=None
checkoutreswid=None

# create database hotel;
# use hotel;
# create table staff(empid int auto_increment primary key,name varchar(50),email varchar(50),password varchar(50),address varchar(150),designation varchar(15),salary real,gender varchar(1),dob date,phno varchar(15),photo longtext,dateofjoin date);
# create table reservations(reservation_id int auto_increment primary key,g_count int,rooms_booked int,rooms_id varchar(100),amount real,add_ons varchar(100),addons_price real default 0,gstatus enum('CHECKIN','CHECKOUT','BOOKED'),dates_booked varchar(30));
# create table guest(guestid int auto_increment primary key,reservation_id int ,g_name varchar(50),phno varchar(15),country varchar(20),gender varchar(1),room int,image longtext,foreign key(reservation_id) references reservations(reservation_id));
# create table rooms(roomid int primary key,floorno int,roomstatus ENUM('Vacant', 'Occupied', 'Under Maintenance') DEFAULT 'Vacant',price real,roomtype varchar(10),roomdesc varchar(100),booked_dates longtext,room_image longtext);
# create table orders(orderid int auto_increment primary key,guestid int,order_list varchar(100),order_update ENUM('Finish','Prep'),o_payment ENUM('Paid','Pending'),price real default 0,foreign key(guestid) references guest(guestid),time datetime);
# create table amenities(amenity_id int primary key,a_name varchar(50),a_description longtext,head_staff int,a_image longtext,phno varchar(15),floorno int,open_timing time,close_timing time,pricing real,foreign key(head_staff) references staff(empid));


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        x=request.form.get('email')
        y=request.form.get('password')
        s="SELECT name,designation FROM staff WHERE email=%s AND password=%s"
        data=(x,y)
        db.execute(s,data)
        result=db.fetchone()
        if result:
            session['username']=x
            session['name']=result[0]
            session['designation']=result[1]
            print(session)
            if session['designation']=='Chef':
                return render_template('options.html')
            else:
                return render_template('manager.html',name=session['name'])
            # return render_template('login.html')
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home')) 
    
@app.route('/logout',methods=['GET','POST'])
def logout():
    if request.method=='POST':
        session.pop('username',None)
        session.pop('name',None)
        session.pop('designation',None)
        print(session)
        return redirect(url_for('home'))
    else:
        return 'Wrong!'
    

@app.route('/addguest',methods=['GET','POST'])
def addguest():
    if request.method=='POST':
        name=request.form.get('fn')
        phno=request.form.get('phno')
        country=request.form.get('country')
        roomid=int(request.form.get('roomid'))
        reservation=int(request.form.get('reservation'))
        gender=request.form.get('gender')
        image=request.files['file']
        binary_image = image.read() 
        encoded_image = base64.b64encode(binary_image).decode('utf-8')
        # db.execute('insert into guest (reservation_id,g_name,phno,country,gender,room,image) values (%d,%s,%s,%s,%s,%s,%s);',(reservation,name,phno,country,gender,roomid,encoded_image))
        # myconn.commit()
        query = 'INSERT INTO guest (reservation_id, g_name, phno, country, gender, room, image) VALUES (%s, %s, %s, %s, %s, %s, %s);'
        values = (reservation, name, phno, country, gender, roomid, encoded_image)
        # Execute the query
        db.execute(query, values)
        db.execute('update rooms set roomstatus="Occupied" where roomid=%s',(roomid,))
        myconn.commit()
        return render_template('manager.html',name=session['name'],latestreserv=reservationid)
    
@app.route('/reservations',methods=['GET','POST'])
def reservation():
    if request.method=='POST':
        gcount=int(request.form.get('count'))
        totalroom=int(request.form.get('trid'))
        roomid=int(request.form.get('rid'))
        amount=int(request.form.get('amt'))
        # datefrom = datetime.strptime(request.form.get('from'), '%Y-%m-%d')
        # datetill = datetime.strptime(request.form.get('till'), '%Y-%m-%d')
        # fullstr = f"{datefrom},{datetill}"
        datefrom=request.form.get('from')
        datetill=request.form.get('till')
        fullstr=datefrom+","+datetill
        newstr="BOOKED"
        print(gcount)
        print(totalroom)
        print(roomid)
        print(amount)
        print(newstr)
        print(fullstr)
        query = 'INSERT INTO reservations (g_count, rooms_booked, rooms_id, amount, gstatus, dates_booked) VALUES (%s, %s, %s, %s, %s, %s)'
        values = (gcount, totalroom, roomid, amount, newstr, fullstr)
        db.execute(query, values)
        myconn.commit()
        db.execute('select max(reservation_id) from reservations')
        result=db.fetchone()
        global reservationid
        reservationid=result[0]
        return render_template('manager.html',name=session['name'],latestreserv=result[0])
        
    
@app.route('/checkout',methods=['GET','POST'])
def checkout():
    if request.method=='POST':
        global checkoutreswid
        resid=int(request.form.get('resid'))
        checkoutreswid=resid
        print(checkoutreswid)
        print(resid)
        db.execute('select sum(price) from orders where reservationid=%s AND o_payment="Pending"',(resid,))
        result=db.fetchall()
        total=0
        if result and result[0][0] is not None:
            total =total+result[0][0]
        db.execute('update reservations set addons_price=%s where reservation_id=%s',(resid,total,))
        myconn.commit()
        db.execute('select amount from reservations where reservation_id=%s and gstatus="CHECKIN"',(resid,))
        result=db.fetchone()
        if result:
            return render_template('billing.html',reswid=resid,amt=result[0],charge=total,tot=total+result[0])
        else:
            return "INVALID!"
    
@app.route('/billed',methods=['GET','POST'])
def billed():
    if request.method=='POST':
        global checkoutreswid,reservationid
        checkoutreswid
        db.execute('update reservations set gstatus="CHECKOUT" where reservation_id=%s;',(checkoutreswid,))
        db.execute('select rooms_id from reservation where reservation_id=%s;',(checkoutreswid,))
        result=db.fetchone()
        roomids = [roomid.strip() for roomid in result[0].split(',')]
        print(roomids)
        for roomid in roomids:
            db.execute('update rooms set roomstatus="Vacant" where roomid=%s;',(roomid,))
        myconn.commit()
        db.execute('update orders set o_payment="Paid" where reservationid=%s;',(checkoutreswid,))
        myconn.commit()
        return render_template('manager.html',name=session['name'],latestreserv=reservationid)
        
        
@app.route('/chef',methods=['GET','POST'])
def chef():
    if request.method=='POST':
        button=request.form.get('submit')
        if button=='orders':
            db.execute('select orderid,order_list,time from orders where order_update="Prep"')
            result=db.fetchall()
            return render_template('orders.html',orders=result)
        elif button=='orderhistory':
            db.execute('select orderid,guestid,order_list,order_update,o_payment,price,time from orders')
            result=db.fetchall()
            print(result)
            return render_template('orderhistory.html',orders=result)
        else:
            return render_template('pricing.html')
    else:
        return 'Wrong!'

@app.route('/orderaction',methods=['GET','POST'])
def orderaction():
    if request.method=='POST':
        button=request.form.get('button')
        print(button)
        db.execute('update orders set order_update="Finish" where orderid = %s',(button,))
        myconn.commit()
        return render_template('options.html')
    else:
        return 'Wrong!'    


if __name__=="__main__":
    app.run(debug=True)
