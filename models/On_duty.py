from migrate_cmd import db
from datetime import datetime


class On_duty(db.Model):
    
    __tablename__ = 'on_duties'
        
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    job_title_id = db.Column(db.Integer, db.ForeignKey('job_titles.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    attendances = db.relationship('Attendance', backref='on_duty',
                                  lazy='dynamic')                          
   
    
    
    
 
        
 
       





