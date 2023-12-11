import flask
from flask import render_template,request,redirect,url_for

import models
from sqlalchemy import func


app = flask.Flask("hrms")
db = models.SQLAlchemy(model_class = models.HRDBBase)

@app.route("/",methods = ["GET","POST"])
def index():
  if flask.request.method == "GET":
    return flask.render_template("index.html")
 
@app.route("/employees")
def employees():
    query = db.select(models.Employee).order_by(models.Employee.firstname)
    users = db.session.execute(query).scalars()
    return flask.render_template("userlist.html", users = users)

  
@app.route("/employees/<int:empid>")
def employee_details(empid):
  employees = db.select(models.Employee).where(models.Employee.empid == empid)
  user = db.session.execute(employees).scalar()
  emp_count = db.select(func.count(models.Employee.empid)).join(models.Leaves,models.Employee.empid == models.Leaves.empid).where(models.Employee.empid==empid)
  leaves = db.session.execute(emp_count).scalar()
  leave_count = db.select(models.Designation.max_leaves).where(models.Designation.jobid == models.Employee.title_id, models.Employee.empid==empid)
  max_leaves = db.session.execute(leave_count).scalar()
  ret = {"employee_id" : user.empid,
         "firstname" : user.firstname,
         "lastname" : user.lastname,
         "title" : user.title.title,
         "email" : user.email,
         "phone" : user.ph_no,
         "leaves": leaves,
         "max_leaves" : max_leaves}         
  return flask.jsonify(ret)

@app.errorhandler(500)   
def page_not_found(error):
    return render_template('500.html'), 500

@app.errorhandler(404)   
def page_not_found(error):
    return render_template('404.html'), 404

@app.route("/addleave/<int:empid>", methods=["GET", "POST"])
def addleave(empid):
  employees = db.select(models.Employee).where(models.Employee.empid == empid)
  user = db.session.execute(employees).scalar()
  if request.method == "POST":
    date = request.form['date']
    reason = request.form['reason'] 
    insert_data = models.Leaves(empid=empid ,date=date, reason=reason)
    db.session.add(insert_data)
    db.session.commit()
    return redirect(url_for("employees"))
  
@app.route("/about")
def about():
  return render_template("about.html")

  
