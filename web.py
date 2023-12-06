import flask


import models
from sqlalchemy import func


app = flask.Flask("hrms")
db = models.SQLAlchemy(model_class = models.HRDBBase)

@app.route("/",methods = ["GET","POST"])
def index():
  if flask.request.method == "GET":
    return flask.render_template("index.html")
  elif flask.request.method == "POST":
    return "POSTED!"
    
@app.route("/employees")
def employees():
  query = db.select(models.employee).order_by(models.employee.firstname)
  users =db.session.execute(query).scalars()
  return flask.render_template("userlist.html",users = users)
  
@app.route("/employees/<int:empid>")
def employee_details(empid):
  query = db.select(models.employee).where(models.employee.empid == empid)
  user = db.session.execute(query).scalar()
  query1 = db.select(func.count(models.employee.empid)).join(models.leaves,models.employee.empid == models.leaves.empid).where(models.employee.empid==empid)
  leaves = db.session.execute(query1).scalar()
  query2 = db.select(models.designation.max_leaves).where(models.designation.jobid == models.employee.title_id, models.employee.empid==empid)
  max_leaves = db.session.execute(query2).scalar()
  return flask.render_template("userdetails.html", user = user, leaves = leaves, max_leaves = max_leaves)
  
@app.route("/addleave",methods=["GET","POST"])
def add_leaves():
  if flask.request.method == "POST":
    empid = flask.request.form['empid']
    date = flask.request.form['date']
    reason = flask.request.form['reason'] 
    query = models.leaves(empid=empid,date=date,reason=reason)
    db.session.add(query)
    db.session.commit()
    return flask.render_template('/')
  return flask.render_template("addleave.html")
  
