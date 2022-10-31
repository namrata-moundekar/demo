from migrate_cmd import db
from datetime import datetime
#######################    MODELS HERE  ########################################

class Department(db.Model):
    
  __tablename__ = 'departments'
  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60), unique=True)
  job_titles = db.relationship('Job_title', backref='department',
                                lazy='dynamic')
  
 
  
  
  







