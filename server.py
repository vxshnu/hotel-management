from flask import Flask,redirect,render_template,request,url_for,session
import mysql.connector
import base64 
from datetime import datetime,timedelta

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
room_status=None
order_status=None
staff_status=None
reserv_status=None

# create database hotel;
# use hotel;
# create table staff(empid int auto_increment primary key,name varchar(50),email varchar(50),password varchar(50),address varchar(150),designation varchar(15),salary real,gender varchar(1),dob date,phno varchar(15),photo longtext,dateofjoin date);
# create table reservations(reservation_id int auto_increment primary key,name varchar(25),g_count int,rooms_booked int,rooms_id varchar(100),amount real,add_ons varchar(100),addons_price real default 0,gstatus enum('CHECKIN','CHECKOUT','BOOKED'),dates_booked varchar(30));
# create table guest(guestid int auto_increment primary key,reservation_id int ,g_name varchar(50),phno varchar(15),country varchar(20),gender varchar(1),room int,image longtext,foreign key(reservation_id) references reservations(reservation_id));
# create table rooms(roomid int primary key,floorno int,roomstatus ENUM('Vacant', 'Occupied', 'Under Maintenance') DEFAULT 'Vacant',price real,roomtype varchar(10),roomdesc varchar(100),booked_dates longtext,room_image longtext);
# create table orders(orderid int auto_increment primary key,reservationid int,order_list varchar(100),order_update ENUM('Finish','Prep'),o_payment ENUM('Paid','Pending'),price real default 0,foreign key(reservationid) references reservations(reservation_id),time datetime);

def refresh():
    db.execute('select roomid,floorno,roomtype,roomdesc,booked_dates,roomstatus,price from rooms;')
    result=db.fetchall()
    global room_status,order_status,staff_status,reserv_status
    room_status=result
    db.execute('select * from orders ORDER BY orderid DESC;')
    result=db.fetchall()
    order_status=result
    db.execute('select empid,name,address,designation,salary,phno,dateofjoin from staff;')
    result=db.fetchall()
    print(result)
    staff_status=result
    db.execute('select * from reservations where gstatus="CHECKIN" OR gstatus="BOOKED" ORDER BY reservation_id DESC;')
    result=db.fetchall()
    reserv_status=result
    
@app.route('/error')
def error():
    global reservationid,checkoutreswid,room_status,order_status,staff_status,reserv_status
    refresh()
    return render_template('manager.html',name=session['name'],latestreserv=reservationid,roomdetails=room_status,ordered=order_status,staffs=staff_status,reservations=reserv_status)


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
                refresh()
                return render_template('manager.html',name=session['name'],latestreserv=reservationid,roomdetails=room_status,ordered=order_status,staffs=staff_status,reservations=reserv_status)
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
        query = 'INSERT INTO guest (reservation_id, g_name, phno, country, gender, room, image) VALUES (%s, %s, %s, %s, %s, %s, %s);'
        values = (reservation, name, phno, country, gender, roomid, encoded_image)
        db.execute(query, values)
        db.execute('update rooms set roomstatus="Occupied" where roomid=%s ',(roomid,))
        db.execute('update reservations set gstatus="CHECKIN" where reservation_id=%s',(reservation,))
        myconn.commit()
        refresh()
        return render_template('manager.html',name=session['name'],latestreserv=reservation,roomdetails=room_status,ordered=order_status,staffs=staff_status,reservations=reserv_status)
               
@app.route('/reservations',methods=['GET','POST'])
def reservation():
    if request.method=='POST':
        gname=request.form.get('gname')
        gcount=int(request.form.get('count'))
        totalroom=int(request.form.get('trid'))
        roomid=request.form.get('rid')
        # amount=int(request.form.get('amt'))
        datefrom=request.form.get('from')
        datetill=request.form.get('till')
        # fullstr=datefrom+","+datetill
        newstr="BOOKED" 
        roomids = [rid.strip() for rid in roomid.split(',')]
        datestring=""
        mainstring=""
        amount=0
        for ids in roomids:
            counter=0
            db.execute('select * from rooms where roomid=%s and roomstatus="Vacant"',(ids,))
            a=db.fetchone()
            if a:
                db.execute('select booked_dates from rooms where roomid=%s;',(ids,))
                result=db.fetchone()
                dates = result[0]
                datefrom1 = datetime.strptime(datefrom, "%Y-%m-%d")
                datetill1 = datetime.strptime(datetill, "%Y-%m-%d")

                current_date = datefrom1
                
                while current_date < datetill1:
                    print(current_date.strftime("%Y-%m-%d"))
                    current_date += timedelta(days=1)
                    datestring+=current_date.strftime("%Y-%m-%d")+","
                    counter+=1
                print(datestring)
                db.execute('select price from rooms where roomid=%s;',(ids,))
                result=db.fetchone()
                amount+=result[0]*counter
                if dates:
                    if datefrom in dates or datetill in dates:
                        myconn.rollback()
                        return render_template("error.html",message="ROOM NOT AVAILABLE!")     
                    dates+=" AND "+datestring
                else:
                    dates=datestring
                db.execute('update rooms set booked_dates=%s where roomid=%s;',(dates,ids,))
                mainstring=datestring
                datestring=""
            else:
                myconn.rollback()
                return render_template("error.html",message="ROOM NOT VACANT!")
        query = 'INSERT INTO reservations (name,g_count, rooms_booked, rooms_id, amount, gstatus, dates_booked) VALUES (%s,%s, %s, %s, %s, %s, %s)'
        values = (gname,gcount, totalroom, roomid, amount, newstr, mainstring)
        db.execute(query, values)
        myconn.commit()
        db.execute('select max(reservation_id) from reservations')
        result=db.fetchone()
        print(result)
        global reservationid
        reservationid=result[0]
        print(reservationid)
        myconn.commit()
        refresh()
        return render_template('manager.html',name=session['name'],latestreserv=reservationid,roomdetails=room_status,ordered=order_status,staffs=staff_status,reservations=reserv_status)
        
    
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
        print(checkoutreswid)
        db.execute('update reservations set gstatus="CHECKOUT" where reservation_id=%s;',(checkoutreswid,))
        db.execute('select rooms_id from reservations where reservation_id=%s;',(checkoutreswid,))
        result=db.fetchone()
        print(result)
        roomids = [roomid.strip() for roomid in result[0].split(',')]
        print(roomids)
        for roomid in roomids:
            db.execute('update rooms set roomstatus="Vacant" where roomid=%s;',(roomid,))
            db.execute('select dates_booked from reservations where reservation_id=%s;',(checkoutreswid,))
            result=db.fetchone()
            removebookdate=result[0]
            # removebookdate=" AND "+removebookdate
            db.execute('select booked_dates from rooms where roomid=%s;',(roomid,))
            result=db.fetchone()
            resbookdate=result[0]
            if removebookdate in resbookdate:
                removebookdate = resbookdate.replace(removebookdate, "") 
            if "AND" in removebookdate:
                removebookdate = removebookdate.replace("AND", "")
            if removebookdate=="":
                removebookdate=None        
            db.execute('update rooms set booked_dates=%s where roomid=%s;',(removebookdate,roomid,))
        myconn.commit()
        db.execute('update orders set o_payment="Paid" where reservationid=%s;',(checkoutreswid,))
        myconn.commit()
        refresh()
        return render_template('manager.html',name=session['name'],latestreserv=reservationid,roomdetails=room_status,ordered=order_status,staffs=staff_status,reservations=reserv_status)


@app.route('/ordersubmit',methods=['GET','POST'])
def ordersubmit():
    if request.method=='POST':
        resid=request.form.get('resid')
        orderl=request.form.get('orderl')
        price=request.form.get('price')
        print(resid)
        print(orderl)
        print(price)
        db.execute('select reservation_id from reservations where reservation_id=%s',(resid,))
        result=db.fetchone()
        if result:
            db.execute('insert into orders (reservationid,order_list,order_update,o_payment,price,time) values(%s,%s,"Prep","Pending",%s,NOW())',(resid,orderl,price,))
            myconn.commit()
            refresh()
            return render_template('manager.html',name=session['name'],latestreserv=reservationid,roomdetails=room_status,ordered=order_status,staffs=staff_status,reservations=reserv_status)
        else:
            return render_template("error.html",message="INVALID RESERVATION ID!")
 
@app.route('/roomupdate',methods=['GET','POST'])
def roomupdate():
    if request.method=='POST':
        roomid=request.form.get('RoomId')
        status=request.form.get('SU')
        price=request.form.get('CP')
        print(price)
        if status and price:
            db.execute('update rooms set price=%s where roomid=%s;',(price,roomid,))
            db.execute('update rooms set roomstatus=%s where roomid=%s;',(status,roomid,))
        elif status:
            db.execute('update rooms set roomstatus=%s where roomid=%s;',(status,roomid,))
        elif price:
            db.execute('update rooms set price=%s where roomid=%s;',(price,roomid,))
        myconn.commit()
        refresh()
        return render_template('manager.html',name=session['name'],latestreserv=reservationid,roomdetails=room_status,ordered=order_status,staffs=staff_status,reservations=reserv_status)


@app.route('/addstaff',methods=['GET','POST'])
def addstaff():
    if request.method=='POST':
        name=request.form.get('nam')
        email=request.form.get('emailadd')
        password=request.form.get('pass')
        address=request.form.get('addr')
        designation=request.form.get('desgn')
        salary=request.form.get('sal')
        gender=request.form.get('g')
        dob=request.form.get('dob')
        phone=request.form.get('phn')
        photo=request.files['photo']
        doj=request.form.get('doj')
        
        binary_image = photo.read() 
        encoded_image = base64.b64encode(binary_image).decode('utf-8')
        db.execute('insert into staff (name,email,password,address,designation,salary,gender,dob,phno,photo,dateofjoin) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);',(name,email,password,address,designation,salary,gender,dob,phone,encoded_image,doj,))
        myconn.commit()
        refresh()
        
        return render_template('manager.html',name=session['name'],latestreserv=reservationid,roomdetails=room_status,ordered=order_status,staffs=staff_status,reservations=reserv_status)


@app.route('/updatestaff',methods=['GET','POST'])
def updatestaff():
    if request.method=='POST':
        eid=request.form.get('eid')
        button=request.form.get('buttons')
        db.execute('select empid from staff where empid=%s',(eid,))
        result=db.fetchone()
        if result:
            if button=='update':
                dropdown=request.form.get('selectField')
                text=request.form.get('addField')
                s=f"update staff set {dropdown}=%s where empid=%s;"
                data=(text,eid,)
                db.execute(s,data)
                myconn.commit()
            else:
                db.execute('delete from staff where empid=%s;',(eid,))
                myconn.commit()
            refresh()
            return render_template('manager.html',name=session['name'],latestreserv=reservationid,roomdetails=room_status,ordered=order_status,staffs=staff_status,reservations=reserv_status)
        else:
            return render_template("error.html",message="INVALID EMPLOYEE ID!")
            
        
 
@app.route('/chef',methods=['GET','POST'])
def chef():
    if request.method=='POST':
        button=request.form.get('submit')
        if button=='orders':
            db.execute('select orderid,order_list,time from orders where order_update="Prep"')
            result=db.fetchall()
            return render_template('orders.html',orders=result)
        elif button=='orderhistory':
            db.execute('select orderid,reservationid,order_list,order_update,o_payment,price,time from orders ORDER BY orderid DESC;')
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
        db.execute('select orderid,order_list,time from orders where order_update="Prep"')
        result=db.fetchall()
        return render_template('orders.html',orders=result)
    else:
        return 'Wrong!'    


if __name__=="__main__":
    app.run(debug=True)
