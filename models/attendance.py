from migrate_cmd import db
from datetime import datetime


class Attendance(db.Model):
    
    __tablename__ = 'attendances'
        
    id = db.Column(db.Integer, primary_key=True)
    total_task = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    status = db.Column(db.String(60))
    job_title_id = db.Column(db.Integer, db.ForeignKey('job_titles.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    leave_id = db.Column(db.Integer, db.ForeignKey('leaves.id'))                          
    on_duty_id = db.Column(db.Integer, db.ForeignKey('on_duties.id'))
                              
   
    
    
    
 
        
 
       





