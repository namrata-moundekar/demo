from migrate_cmd import db
from datetime import datetime


class Leave(db.Model):
    
    __tablename__ = 'leaves'
        
    id = db.Column(db.Integer, primary_key=True)
    leave_date = db.Column(db.DateTime)
    job_title_id = db.Column(db.Integer, db.ForeignKey('job_titles.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    attendances = db.relationship('Attendance', backref='leave',
                                  lazy='dynamic') 
    
    
    
 
        
 
       





