from flask import Flask, jsonify, send_from_directory
from marshmallow import Schema, fields
from werkzeug.utils import secure_filename
import datetime
import calendar
import json
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import check_password_hash
from flask import jsonify
from flask_marshmallow import Marshmallow, fields
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import os
import logging
from flask_restful import Resource
from flask import Blueprint, Response, request
from pathlib import Path
from urllib.parse import urljoin
from flask import current_app
from flask import make_response
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint 
from migrate_cmd import db, migrate

from models.employee import Employee
from models.department import Department
from models.job_title import Job_title
from models.On_duty import On_duty
from models.leave import Leave
from models.attendance import Attendance

from ast import literal_eval
from flask_caching import Cache



#######################     Logging Starts   ######################################
logging.basicConfig(filename='Employee_attendance_log.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s : %(message)s')

#######################    APP CONFIG HERE  ########################################
"""      app config here    """


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:root@localhost/emp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False


######################    Caching CONFIG HERE  ########################################
"""      Caching config here    """

cache = Cache(config = {
    "DEBUG": True,         
    "CACHE_TYPE": "SimpleCache",  
    "CACHE_DEFAULT_TIMEOUT": 300
})



ma = Marshmallow(app)
api = Api(app)
cache.init_app(app)
db.init_app(app)

migrate.init_app(app, db)



app.config["JWT_SECRET_KEY"] = "TOKEN"
jwt = JWTManager(app)



######################    MODELS SCHEMA USING MARSHMALLOW HERE  ########################################




class AttendanceSchema(ma.Schema):
    class Meta:
        model = Attendance
        load_instance = True
        include_relationships = True
        fields = ("id","total_task", "date","status","employee_id")    


class On_dutySchema(ma.Schema):
    class Meta:
        model = On_duty
        load_instance = True
        include_relationships = True
        fields = ("id","duration", "date","job_title_id","employee_id","attendances")
    attendances = ma.Nested(AttendanceSchema, many=True)


    
class LeaveSchema(ma.Schema):
    class Meta:
        model = Leave
        load_instance = True
        include_relationships = True
        fields = ("id","leave_date", "job_title_id","employee_id","attendances")
    attendances = ma.Nested(AttendanceSchema, many=True)

class Job_titleSchema(ma.Schema):
    class Meta:
        model = Job_title
        load_instance = True
        include_relationships = True
        fields = ("id","job_title","salary","department_id","employee_id","leaves")
    leaves = ma.Nested(LeaveSchema, many=True)
    
class DepartmentSchema(ma.Schema):
    class Meta:
        model = Department
        load_instance = True
        include_relationships = True
        fields = ("id","name","job_titles")
    job_titles = ma.Nested(Job_titleSchema, many=True)        

class EmployeeSchema(ma.Schema):
    class Meta:
        model = Employee
        load_instance = True
        include_relationships = True
        fields = ("id","username", "password","email","first_name","last_name","gender","age","contact_no","job_titles")
    job_titles = ma.Nested(Job_titleSchema, many=True)
    # on_duties = ma.Nested(On_dutySchema, many=True)
    
    
    
attendance_schema = AttendanceSchema()
attendances_schema = AttendanceSchema(many=True)

on_duty_schema = On_dutySchema()
on_duties_schema = On_dutySchema(many=True)

leave_schema = LeaveSchema()
leaves_schema = LeaveSchema(many=True)

job_title_schema = Job_titleSchema()
job_titles_schema = Job_titleSchema(many=True)
    
employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

department_schema = DepartmentSchema()
departments_schema = DepartmentSchema(many=True)




###############################   Bluprint specific  ####################################################

employee_blueprint = Blueprint('employee_blueprint', __name__)
department_blueprint = Blueprint('department_blueprint', __name__)
job_title_blueprint = Blueprint('job_title_blueprint', __name__)
on_duty_blueprint = Blueprint('on_duty_blueprint', __name__)
leave_blueprint = Blueprint('leave_blueprint', __name__)
attendance_blueprint = Blueprint('attendance_blueprint', __name__)



##############################   swagger specific  ####################################################


SWAGGER_URL = '/swagger/'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "EmployeeRestAPIFlask"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

###########################      End swagger specific     #################################################




# ##########################     Employee REGISTER AND LOGIN CODE HERE     #####################################

@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def welcome():
    return "welcome to home page"



@employee_blueprint.route('/get_emp/', methods = ['POST'])
def emp_register():
    """ REGISTER USER WITH USERNAME AND PASSWORD"""
    
    data = request.get_json()  # will retrive that json
    if data:
        if data.get('id'):
            id = data.get('id')
            emp = Employee.query.filter_by(id=id).first()
            if emp:
                return json.dumps({"ERROR" : "Duplicate employee -->401"})
            emp_data = Employee(id=data["id"],username=data["username"],password=generate_password_hash(data["password"]),email=data["email"],first_name=data["first_name"],last_name=data["last_name"],gender=data["gender"],age=data["age"],contact_no=data["contact_no"])
            db.session.add(emp_data)
            db.session.commit()
            app.logger.info("Department added successfully")
            return json.dumps({"SUCCESS" : f"Record ({emp_data.id}) Added Successfully...! 200"})

        return json.dumps({"ERROR": "Required fields not present"})
    else:
        return json.dumps({"ERROR" : "EMPTY BODY, ALL FIELDS REQUIRED"})
   


@employee_blueprint.route('/emp_login/', methods = ['GET','POST'])
def emp_login():
    """ LOGIN WITH USER NAME AND PASSWORD AND IT RETURNS BEARER ACCESS TOKEN"""
    
    data = request.get_json()  # will retrive that json
    if data:
        if data.get('id') and data.get('username') and data.get('password'):
            username = data.get('username')
            password= data.get('password')
            user = Employee.query.filter_by(username=username).first()
            print("sss",user)
            if check_password_hash(user.password,data.get('password')):
                print("password")
                token = create_access_token(identity=user.username)
                print("token",token)
                app.logger.info("Get token when login")
                return json.dumps({"token":token})
                    
        else:
                return json.dumps({"ERROR":"Invalid name or password"})    
    

@employee_blueprint.route('/get_emp/', methods = ['GET'])
@jwt_required()
def get_emp_all():
    """  Get List of emp  """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    all_emp = Employee.query.all()
    print("all_user after",all_emp)
    app.logger.info("Get all user")
    return employees_schema.dump(all_emp)

@employee_blueprint.route('/emp/<int:id>',methods=['GET'])
@jwt_required()
def get_emp(id):
    """ GET emp POST USING ID"""
    
    emp = Employee.query.filter_by(id=id).first()
    if emp:
        json_dict = {"emp_ID": emp.id,
                      "emp_username": emp.username,
                      "emp_password": emp.password,
                      "emp_email": emp.email,
                      "emp_first_name": emp.first_name,
                      "emp_last_name": emp.last_name,
                      "emp_gender": emp.gender,
                      "emp_age": emp.age,
                      "emp_contact": emp.contact_no
                      }
        app.logger.info("Get Employee with particular id")
        return json.dumps(json_dict,indent=4, sort_keys=True, default=str)
    else:
        return json.dumps({"ERROR": f"No Employee with Given Id {id}"})
    
@employee_blueprint.route('/emp/<int:id>',methods=['PUT'])
@jwt_required()
def update_emp(id):
    """ UPDATE Department POST"""
    
    emp = Employee.query.filter_by(id=id).first()
    if emp:
        data = request.get_json()
        if data:
            if data.get('username') and data.get('password') and data.get('email') and data.get('first_name') and data.get('last_name') and data.get('gender') and  data.get('age') and data.get('contact_no'):
                emp.username = data.get('username')
                emp.password = data.get('password')
                emp.email = data.get('email')
                emp.first_name = data.get('first_name')
                emp.last_name = data.get('last_name')
                emp.gender = data.get('gender')
                emp.age = data.get('age')
                emp.contact_no = data.get('contact_no')
                db.session.commit()
                app.logger.info("Employee updated successfully")
                return json.dumps({"SUCCESS" : f"Record ({emp.id}) Updated Successfully...!  200"})
        return json.dumps({"ERROR": "Required fields not present"})
    return json.dumps({"ERROR": "emp with given id not present so cannot update.."})


@employee_blueprint.route('/emp/search/', methods = ['POST'])
@jwt_required()
@cache.cached(timeout=30)
def search_emp():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    data = request.get_json()
    if data.get('username'):
            search_username = data.get('username')
            emp = Employee.query.filter_by(username=search_username).all()
    
    if data.get('email'):
            search_email = data.get('email')
            emp = Employee.query.filter_by(email=search_email).all()
     
    if not emp:
        return json.dumps({"ERROR": "Employee not present"})

    return employees_schema.dump(emp)
    
 
@employee_blueprint.route('/emp/<int:id>',methods=['DELETE'])
@jwt_required()
def delete_emp(id):
    """ DELETE emp POST """
    
    emp = Employee.query.filter_by(id=id).first()
    if emp:
        db.session.delete(emp)
        db.session.commit()
        app.logger.info("Employee deleted successfully")
        return json.dumps({"SUCCESS": f"Record ({id}) Removed Successfully...! 200"})
    return json.dumps({"ERROR": "Employee with given id not present so cannot Delete.."})


    
 
  

# ##########################    DEPARTMENT START HERE     #############################################

@department_blueprint.route('/get_dept/', methods = ['POST'])
@jwt_required()
def add_dept():
    """ ADD dept WITH BEARER TOKEN"""
    
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    data = request.get_json()
    if data:
        if data.get('id'):
            id = data.get('id')
            dept = Department.query.filter_by(id=id).first()
            if dept:
                return json.dumps({"ERROR" : "Duplicate Department -->401"})
            depart = Department(**data)
            db.session.add(depart)
            db.session.commit()
            app.logger.info("Department added successfully")
            return json.dumps({"SUCCESS" : f"Record ({depart.id}) Added Successfully...! 200"})

        return json.dumps({"ERROR": "Required fields not present"})
    else:
        return json.dumps({"ERROR" : "EMPTY BODY, ALL FIELDS REQUIRED"})



@department_blueprint.route('/dept/<int:id>',methods=['GET'])
@jwt_required()
def get_dept(id):
    """ GET dept POST USING ID"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    dept = Department.query.filter_by(id=id).first()
    if dept:
        json_dict = {"Department_ID": dept.id,
                      "Department_name": dept.name,
                     
                      }
        app.logger.info("Get Department with particular id")
        return json.dumps(json_dict,indent=4, sort_keys=True, default=str)
    else:
        return json.dumps({"ERROR": f"No Department with Given Id {id}"})




@department_blueprint.route('/get_all_dept/', methods = ['GET'])
@jwt_required()
def get_all_dept():
    """Get List of Department"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    all_dept = Department.query.all()
    app.logger.info("Get all departments post")
    return departments_schema.dump(all_dept)
    
    
    

@department_blueprint.route('/dept/<int:id>',methods=['PUT'])
@jwt_required()
def update_dept(id):
    """ UPDATE Department POST"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    dept = Department.query.filter_by(id=id).first()
    if dept:
        data = request.get_json()
        if data:
            if data.get('name') :
                dept.name = data.get('name')
                
                db.session.commit()
                app.logger.info("Department updated successfully")
                return json.dumps({"SUCCESS" : f"Record ({dept.id}) Updated Successfully...!  200"})
        return json.dumps({"ERROR": "Required fields not present"})
    return json.dumps({"ERROR": "Department with given id not present so cannot update.."})


@department_blueprint.route('/dept/search/', methods = ['POST'])
@jwt_required()
@cache.cached(timeout=30)
def search_dept():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    data = request.get_json()
    if data.get('name'):
            search_name = data.get('name')
            dept = Department.query.filter_by(name=search_name).all()
    
    
     
    if not dept:
        return json.dumps({"ERROR": "Department not present"})

    return departments_schema.dump(dept)
    
 
@department_blueprint.route('/dept/<int:id>',methods=['DELETE'])
def delete_dept(id):
    """ DELETE BLOG POST """
    
    dept = Department.query.filter_by(id=id).first()
    if dept:
        db.session.delete(dept)
        db.session.commit()
        app.logger.info("Department deleted successfully")
        return json.dumps({"SUCCESS": f"Record ({id}) Removed Successfully...! 200"})
    return json.dumps({"ERROR": "Department with given id not present so cannot Delete.."})



# ##########################################  Job Title START HERE  ########################################################



@job_title_blueprint.route('/post_job/', methods = ['POST'])
@jwt_required()
def add_job():
    """Post List of role """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    data = request.get_json()
    if data:
        if data["id"]:
            job = Job_title.query.filter_by(id=data["id"]).first()
            if job:
                return json.dumps({"ERROR" : "employee with Duplicate job-->401"})
            rol = Job_title(id=data["id"],job_title=data["job_title"],salary=data["salary"],department_id=data["department_id"],employee_id=data["employee_id"])
            db.session.add(rol)
            db.session.commit()
            app.logger.info("Job added successfully")
            return json.dumps({"SUCCESS" : f"Record ({rol.id}) Added Successfully...!  200"})
        return json.dumps({"ERROR": "Required fields not present"})
    else:
        return json.dumps({"ERROR" : "EMPTY BODY, ALL FIELDS REQUIRED"})


@on_duty_blueprint.route('/post_onduty/', methods = ['POST'])
@jwt_required()
def add_onduty():
    """Post List of role """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    data = request.get_json()
    if data:
        if data["id"]:
            duty = On_duty.query.filter_by(id=data["id"]).first()
            if duty:
                return json.dumps({"ERROR" : "employee with Duplicate job-->401"})
            onduty = On_duty(id=data["id"],duration=data["duration"],date=data["date"],employee_id=data["employee_id"],job_title_id=data["job_title_id"])
            db.session.add(onduty)
            db.session.commit()
            app.logger.info("On duty time added successfully")
            return json.dumps({"SUCCESS" : f"Record ({onduty.id}) Added Successfully...!  200"})
        return json.dumps({"ERROR": "Required fields not present"})
    else:
        return json.dumps({"ERROR" : "EMPTY BODY, ALL FIELDS REQUIRED"})


@leave_blueprint.route('/post_leave/', methods = ['POST'])
@jwt_required()
def add_leave():
    """Post List of role """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    data = request.get_json()
    if data:
        if data["id"]:
            leave = Leave.query.filter_by(id=data["id"]).first()
            if leave:
                return json.dumps({"ERROR" : "employee with already leave on this date->401"})
            leave = Leave(id=data["id"],leave_date=data["leave_date"],employee_id=data["employee_id"],job_title_id=data["job_title_id"])
            db.session.add(leave)
            db.session.commit()
            app.logger.info("On duty time added successfully")
            return json.dumps({"SUCCESS" : f"Record ({leave.id}) Added Successfully...!  200"})
        return json.dumps({"ERROR": "Required fields notleave present"})
    else:
        return json.dumps({"ERROR" : "EMPTY BODY, ALL FIELDS REQUIRED"})

@attendance_blueprint.route('/post_attend/', methods = ['POST'])
@jwt_required()
def add_attend():
    """Post List of role """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    data = request.get_json()
    # if data:
        # if data["id"]:
            # attend = Attendance.query.filter_by(id=data["id"]).first()
            # if attend:
            #     return json.dumps({"ERROR" : "employee with duplicate attend on this date->401"})
    attendc = Attendance(id=data["id"],total_task=data["total_task"],date=data["date"],status=data["status"],employee_id=data["employee_id"],job_title_id=data["job_title_id"],leave_id=data["leave_id"],on_duty_id=data["on_duty_id"])
    db.session.add(attendc)
    db.session.commit()
    app.logger.info("On duty time added successfully")
    return json.dumps({"SUCCESS" : f"Record ({attendc.id}) Added Successfully...!  200"})
# return json.dumps({"ERROR": "Required fields notleave present"})
# else:
# return json.dumps({"ERROR" : "EMPTY BODY, ALL FIELDS REQUIRED"})


@attendance_blueprint.route('/attend_info/<int:id>',methods=['GET'])
@jwt_required()
def get_attend(id):
    """role detail view."""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    role = Attendance.query.filter_by(id=id).first()
    if role:
        json_dict = {"role_ID": role.id,
                      "role_total task": role.total_task,
                      "role_date": role.date,
                      "emp_status": role.status,
                      "role_job_title": role.job_title_id,
                      "role_employeename": role.employee_id,
                      "role_leave": role.leave_id,
                      "grade_on_duty_id": role.on_duty_id,
                      
                
                      }
        app.logger.info("Get role with particular id.")
        return attendance_schema.dump(role)
    else:
        return json.dumps({"ERROR": f"No role with Given Id {id}"})

  

@job_title_blueprint.route('/get_job/',methods=['GET'])
@cache.cached(timeout=30)
@jwt_required()
def get_job_all():
    """Get List of job"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    all_job= Job_title.query.all()
    
    app.logger.info("Get all role ")
    return job_titles_schema.dump(all_job) 


@leave_blueprint.route('/get_leave/',methods=['GET'])
@cache.cached(timeout=30)
@jwt_required()
def get_leave_all():
    """Get List of job"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    all_job= Leave.query.all()
    
    app.logger.info("Get all role ")
    return leaves_schema.dump(all_job) 



@attendance_blueprint.route('/get_attend/',methods=['GET'])
@cache.cached(timeout=30)
@jwt_required()
def get_attend_all():
    """Get List of job"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    allattend= Attendance.query.all()
    
    app.logger.info("Get all role ")
    return attendances_schema.dump(allattend)  


@attendance_blueprint.route('/view_attend/<int:id>',methods=['GET'])
@jwt_required()
def view_attendance(id):
    """Get List of attendances of particular employee"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    
    role = Attendance.query.filter_by(employee_id=id).all()
    leave = Leave.query.filter_by(employee_id=id).all()
    # print("attendance",role.__dict__)
    # print("leave",leave.__dict__)
    for i in role:
        for j in leave:
            if i.date== j.leave_date:
                
                if i.status=="present" or i.status=="leave":
                    i.status="leave"
                    db.session.commit()
                    
        if i.total_task < 9:
            i.status="half day"
        
        born = datetime.datetime.strptime(str(i.date), '%Y-%m-%d %H:%M:%S').weekday()
        if calendar.day_name[born] == "Saturday" or calendar.day_name[born]== "Sunday":
            i.status="weekend"
            
        db.session.commit()      
    return attendances_schema.dump(role)  






 
# def findDay(date):
#     born = datetime.datetime.strptime(date, '%d %m %Y').weekday()
#     return (calendar.day_name[born])
 
# # Driver program
# date = '03 02 2019'
# print(findDay(date))






# @role_blueprint.route('/role_update/<int:id>',methods=['PUT'])
# @jwt_required()
# def update_role(id):
#     """ UPDATE role POST """
#     current_user = get_jwt_identity()
#     access_token = create_access_token(identity = current_user)
#     role = Role.query.filter_by(id=id).first()
#     if role:
#         data = request.get_json()
#         if data:
#             if data.get('name') and data.get('description') and data.get('grade_id') :
#                 role.name = data.get('name')
#                 role.description = data.get('description')
#                 role.grade_id = data.get('grade_id')
                
#                 db.session.commit()
#                 app.logger.info("role updated successfully")
#                 return json.dumps({"SUCCESS" : f"Record ({role.id}) Updated Successfully...!  200"})
#         return json.dumps({"ERROR": "Required fields not present"})
#     return json.dumps({"ERROR": "role with given id not present so cannot update.."})


# @role_blueprint.route('/role/search/', methods=['POST'])
# @jwt_required()
# @cache.cached(timeout=30)
# def search_role():
#     current_user = get_jwt_identity()
#     access_token = create_access_token(identity=current_user)
#     data = request.get_json()

#     if data.get('name'):
#             search_role = data.get('name')
#             role = Role.query.filter_by(name=search_role).all()
     
#     if not role:
#         return json.dumps({"ERROR": "Role not present"})

#     return roles_schema.dump(role)



# @role_blueprint.route('/role/<int:id>',methods=['DELETE'])
# def delete_role(id):
#     """ DELETE Role POST """
    
#     role = Role.query.filter_by(id=id).first()
#     if role:
#         db.session.delete(role)
#         db.session.commit()
#         app.logger.info("Role deleted successfully")
#         return json.dumps({"SUCCESS": f"Record ({id}) Removed Successfully...! 200"})
#     return json.dumps({"ERROR": "Role with given id not present so cannot Delete.."})




# ##########################################  Grade START HERE  ########################################################



# @grade_blueprint.route('/post_grade/', methods = ['POST'])
# @jwt_required()
# def add_grade():
#     """Post List of grade """
#     current_user = get_jwt_identity()
#     access_token = create_access_token(identity = current_user)
#     data = request.get_json()  # will retrive that json
#     if data:
#         if data["id"]:
#             grade = Grade.query.filter_by(id=data["id"]).first()
#             if grade:
#                 return json.dumps({"ERROR" : "Duplicate grade-->401"})
#             grde = Grade(id=data["id"],paygrade=data["paygrade"],amount=data["amount"])
#             db.session.add(grde)
#             db.session.commit()
#             app.logger.info("Grade added successfully")
#             return json.dumps({"SUCCESS" : f"Record ({grde.id}) Added Successfully...!  200"})
#         return json.dumps({"ERROR": "Required fields not present"})
#     else:
#         return json.dumps({"ERROR" : "EMPTY BODY, ALL FIELDS REQUIRED"})




# @grade_blueprint.route('/grade_info/<int:id>',methods=['GET'])
# @cache.cached(timeout=30)
# @jwt_required()
# def get_grade(id):
#     """grade detail view."""
#     current_user = get_jwt_identity()
#     access_token = create_access_token(identity=current_user)
#     grade = Grade.query.filter_by(id=id).first()
#     if grade:
#         json_dict = {"grade_ID": grade.id,
#                       "paygrade": grade.paygrade,
#                       "amount": grade.amount,
#                       }
#         app.logger.info("Get grade with particular id.")
#         return grade_schema.dump(grade)
#     else:
#         return json.dumps({"ERROR": f"No grade with Given Id {id}"})

  

# @grade_blueprint.route('/get_grade/',methods=['GET'])
# @cache.cached(timeout=30)
# @jwt_required()
# def get_grade_all():
#     """Get List of Grade"""
#     current_user = get_jwt_identity()
#     access_token = create_access_token(identity=current_user)
#     all_grade= Grade.query.all()
    
#     app.logger.info("Get all Grade ")
#     return grades_schema.dump(all_grade) 
    

# @grade_blueprint.route('/grade_update/<int:id>',methods=['PUT'])
# @jwt_required()
# def update_grade(id):
#     """ UPDATE grade POST """
#     current_user = get_jwt_identity()
#     access_token = create_access_token(identity=current_user)
#     grade = Grade.query.filter_by(id=id).first()
#     if grade:
#         data = request.get_json()
#         if data:
#             if data.get('paygrade') and data.get('amount'):
#                 grade.paygrade = data.get('paygrade')
#                 grade.amount = data.get('amount')
#                 db.session.commit()
#                 app.logger.info("grade updated successfully")
#                 return json.dumps({"SUCCESS" : f"Record ({grade.id}) Updated Successfully...!  200"})
#         return json.dumps({"ERROR": "Required fields not present"})
#     return json.dumps({"ERROR": "grade with given id not present so cannot update.."})


# @grade_blueprint.route('/grade/search/', methods=['POST'])
# @jwt_required()
# @cache.cached(timeout=30)
# def search_grade():
#     current_user = get_jwt_identity()
#     access_token = create_access_token(identity=current_user)
#     data = request.get_json()

#     if data.get('paygrade'):
#             search_paygrade = data.get('paygrade')
#             grade = Grade.query.filter_by(paygrade=search_paygrade).all()
            
#     if data.get('amount'):
#             search_amount = data.get('amount')
#             grade = Grade.query.filter_by(amount=search_amount).all()
     
#     if not grade:
#         return json.dumps({"ERROR": "Grade not present"})

#     return grades_schema.dump(grade)



# @grade_blueprint.route('/grade/<int:id>',methods=['DELETE'])
# def delete_grade(id):
#     """ DELETE grade POST """
    
#     grade = Grade.query.filter_by(id=id).first()
#     if grade:
#         db.session.delete(grade)
#         db.session.commit()
#         app.logger.info("Grade deleted successfully")
#         return json.dumps({"SUCCESS": f"Record ({id}) Removed Successfully...! 200"})
#     return json.dumps({"ERROR": "Grade with given id not present so cannot Delete.."})


# ################################    End of Comment API Endpoints      #########################






# #########################################  Blueprint register routes  ########################################################
app.register_blueprint(employee_blueprint) 

app.register_blueprint(department_blueprint) 

app.register_blueprint(job_title_blueprint)

app.register_blueprint(on_duty_blueprint)

app.register_blueprint(leave_blueprint)

app.register_blueprint(attendance_blueprint)

if __name__ == '__main__':
   
    app.run(host="0.0.0.0", debug=True)