from flask import Flask, render_template, request,session,redirect,flash
import mysql.connector
import json
import math

with open('config.json','r') as c:
	params=json.load(c)["params"]

app = Flask(__name__) 
app.secret_key = 'super-secret-key'  
mydb = mysql.connector.connect(
  host=params["host"],
  user=params["user"],
  passwd=params["passwd"],
  database=params["database"]
)
cursor = mydb.cursor()

@app.route('/')
def home():
	sql1="select * from blog "
	cursor.execute(sql1)
	home_post=cursor.fetchall()
	last=math.ceil(len(home_post)/int(params['no_of_post']))
	page=request.args.get('page')
	if(not str(page).isnumeric()):
		page=1
	page=int(page)
	home_post=home_post[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]
	if(page==1):
		prev="#"
		next="/?page="+str(page+1)
	elif(page==last):
		next="#"
		prev="/?page="+str(page-1)
	else:
		prev="/?page="+str(page-1)
		next="/?page="+str(page+1)

	
	return render_template("index.html",params=params,post=home_post ,prev=prev,next=next)
	
    
    
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
	if('user' in session and session['user']==params["admin_user"]):
		sql="select slno,title,date from blog"
		cursor.execute(sql)
		post=cursor.fetchall()
		return render_template("dashboard.html",params=params,post=post)

	if(request.method=='POST'):
		user=request.form['user']
		passwd=request.form['password']
		if(user==params["admin_user"] and passwd==params['admin_pass']):
			session['user']=user
			sql="select slno,title,date from blog"
			cursor.execute(sql)
			post=cursor.fetchall()
			return render_template("dashboard.html",params=params,post=post)
		else:
			return render_template("login.html",params=params)


	else:
		return render_template("login.html",params=params)

    	
@app.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')
	
@app.route('/delete/<string:slno>')
def delete(slno):
	if('user' in session and session['user']==params["admin_user"]):
		sql1="delete from blog where slno=%s"
		cursor.execute(sql1,(slno,))
		mydb.commit()
		
	return redirect('/dashboard')


@app.route('/about')
def about():

	flash("Want your receipe to appear in our site?mail us your receipe in link below","primary")
	return render_template("about.html",params=params)
    
@app.route('/add' ,methods=['GET','POST'])
def add():
	if(request.method=='POST'):
		#add entry to db
		name=request.form['name']
		email=request.form['email']
		phone=request.form['phone']
		item=request.form['item']
		receipe=request.form['receipe']

		sql = "INSERT INTO addblog (name,email,phone,item,receipe) VALUES (%s,%s,%s,%s,%s)"
		entry=(name,email,phone,item,receipe)
		cursor.execute(sql,entry)
		mydb.commit()
		flash("Message Sent","success")
		

	return render_template("add.html",params=params)

@app.route('/contact' ,methods=['GET','POST'])
def contact():
	if(request.method=='POST'):
		#add entry to db
		name=request.form['name']
		email=request.form['email']
		phone=request.form['phone']
		mssg=request.form['mssg']

		sql = "INSERT INTO contact (name,email,phone,mssg) VALUES (%s,%s,%s,%s)"
		entry=(name,email,phone,mssg)
		cursor.execute(sql,entry)
		mydb.commit()
		flash("Message Sent","success")
		

	return render_template("contact.html",params=params)
@app.route('/edit/<string:slno>',methods=['GET','POST'])
def edit(slno):
	if('user' in session and session['user']==params["admin_user"]):
		if(request.method=='POST'):
			title=request.form['title']
			slug=request.form['slug']
			subtitle=request.form['subtitle']
			content=request.form['content']
			image=request.form['image']

			if(slno=='0'):
				sql = "INSERT INTO blog (title,slug,subtitle,content,img) VALUES (%s,%s,%s,%s,%s)"
				entry=(title,slug,subtitle,content,image)
				cursor.execute(sql,entry)
				mydb.commit()
				return redirect('/edit/'+slno)
			else:
				sql = "update blog set title=%s,slug=%s,subtitle=%s,content=%s,image=%s where slno=%s"
				entry=(title,slug,subtitle,content,image,slno)
				cursor.execute(sql,entry)
				mydb.commit()
				return redirect('/edit/'+slno)

		sql1="select * from blog where slno=%s"
		cursor.execute(sql1,(slno,))
		post=cursor.fetchone()

		return render_template('edit.html',params=params,slno=slno,post=post)


	
	
	
    

@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):

	sql1="select * from blog where slug=%s"
	cursor.execute(sql1,(post_slug,))
	post=cursor.fetchone()
	slno=str(post[0])
	
	
	return render_template('post.html',params=params,post=post,slno=slno)
    


app.run(debug="True")


 