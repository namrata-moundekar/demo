from migrate_cmd import db
from datetime import datetime


#######################    MODELS HERE  ########################################

 
        
 
class Employee(db.Model):
    
  __tablename__ = 'employees'
  
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(60), nullable=False,unique=True)
  password = db.Column(db.String(130), nullable=True)
  email = db.Column(db.String(60),unique=True)
  first_name = db.Column(db.String(60))
  last_name = db.Column(db.String(60))
  gender = db.Column(db.String(60))
  age = db.Column(db.Integer)
  contact_no = db.Column(db.String(60))
  job_titles = db.relationship('Job_title', backref='employee',
                                lazy='dynamic')
  on_duties = db.relationship('On_duty', backref='employee',
                                 lazy='dynamic')
  leaves = db.relationship('Leave', backref='employee',
                                 lazy='dynamic')
  attendances = db.relationship('Attendance', backref='employee',
                                lazy='dynamic')
 
# https://www.youtube.com/watch?v=c2ForaiF9ns  

 # https://newtein.github.io/ams/       

# https://itsourcecode.com/uml/employee-attendance-management-system-er-diagram-erd/

# https://flask-user.readthedocs.io/en/latest/data_models.html#roleanduserroledatamodels
