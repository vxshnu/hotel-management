from flask import Flask,redirect,render_template,request,url_for,session
import mysql.connector

myconn = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="root"
)
db=myconn.cursor()
db.execute("USE hotel")

app=Flask(__name__)

app.secret_key = '1234567890'

# create database hotel;
# use hotel;
# create table staff(empid varchar(5) primary key,name varchar(50),email varchar(50),password varchar(50),address varchar(150),designation varchar(15),salary real,gender varchar(1),dob date,phno varchar(15),photo longtext,dateofjoin date);
# create table guest(guestid varchar(10) primary key,g_name varchar(50),phno varchar(15),nationality varchar(10),email varchar(50),gender varchar(1),g_count int,rooms_booked int,rooms_id varchar(100),amount real,add_ons varchar(100),addons_price real default 0,status enum('CHECKIN','CHECKOUT','BOOKED'));
# create table reservations(guest_id varchar(10),reservation_id varchar(10) primary key, foreign key(guest_id) references guest(guestid));
# ~~create table rooms(roomid varchar(5) primary key,floorno int,roomstatus ENUM('Vacant', 'Occupied', 'Under Maintenance') DEFAULT 'Vacant',price real,roomtype varchar(10),roomdesc varchar(100),booked_dates longtext,room_image longtext,reservation_id varchar(10), foreign key(reservation_id) references reservations (reservation_id));
# create table rooms(roomid varchar(5) primary key,floorno int,roomstatus ENUM('Vacant', 'Occupied', 'Under Maintenance') DEFAULT 'Vacant',price real,roomtype varchar(10),roomdesc varchar(100),booked_dates longtext,room_image longtext);
# ~~create table orders(orderid varchar(10) primary key,guestid varchar(10),order_list varchar(100),o_status ENUM('Paid','Finish','Pending','Prep'),price real default 0,foreign key(guestid) references guest(guestid));
# create table orders(orderid varchar(10) primary key,guestid varchar(10),order_list varchar(100),order_update ENUM('Finish','Prep'),o_payment ENUM('Paid','Pending'),price real default 0,foreign key(guestid) references guest(guestid),time datetime);
# create table amenities(amenity_id varchar(5) primary key,a_name varchar(50),a_description longtext,head_staff varchar(5),a_image longtext,phno varchar(15),floorno int,open_timing time,close_timing time,pricing real,foreign key(head_staff) references staff(empid));


# insert into staff values('I0001','Arun','arun@gmail.com','12345','Nagar, Pattom, Trivandrum','Manager',80000,'M','2000-05-15','1234567890','ABCD','2020-01-07');
# insert into staff values('I0002','Sid','chef@gmail.com','12345','Nagar, Pattom, Trivandrum','Chef',80000,'M','2003-08-04','1234567890','ABCD','2020-01-07');
# insert into guest values('G01','Vishnu N','9496924421','Indian','vishnunarayanan@gmaill.com','M',1,1,'R150',0,'0',0,'CHECKIN');
# insert into rooms values('R150',1,'Occupied',5000,'Delux','Lorem Ipsum Lorem Ipsum Lorem Ipsum','0','0');
# insert into orders values('O001','G01','LOREM IPSUM,LOREM IPSUM,LOREM','Prep','Pending',1001,NOW());
# insert into orders values('O002','G01','LOREM,LOREM IPSUM,LOREM','Finish','Pending',500,NOW());


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
                return redirect(url_for(home))
            # return render_template('login.html')
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home')) 
    
    
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
