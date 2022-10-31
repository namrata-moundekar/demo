from migrate_cmd import db
from datetime import datetime


class Job_title(db.Model):
    
    __tablename__ = 'job_titles'
    
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(60))
    salary = db.Column(db.Integer)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    leaves = db.relationship('Leave', backref='job_title',
                                   lazy='dynamic')
    attendances = db.relationship('Attendance', backref='job_title',
                                  lazy='dynamic')
    
 
        
 
       





