from flask import Blueprint, Response, request
from migrate_cmd import db
from model_schema import Employee,Department,Job_title,Leave,Attendance
from model_schema import department_schema,departments_schema
from model_schema import employee_schema,employees_schema
from model_schema import job_title_schema,job_titles_schema
from model_schema import leave_schema,leaves_schema
from model_schema import attendance_schema,attendances_schema
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import json
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from migrate_cmd import redis_cache
from ast import literal_eval
from constants import EMP_LIST
from constants import DEPART_LIST
from constants import LEAVE_LIST
import time
from flask import jsonify
from celery import Celery
import logging

simple_app = Celery('tasks', backend='redis://localhost:6379/0',
                    broker='amqp://namrata:namrata.31@localhost/neosoft_vhost')

#######################     Logging Starts   ######################################
logging.basicConfig(filename='Employee_attendance_log.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s : %(message)s')

######################    CELERY AND RABBITMQ    ########################################

# @app.route('/simple_start_task')
# def call_method():
#     app.logger.info("Invoking Method ")
#     r = simple_app.send_task('tasks.longtime_add', kwargs={'x': 1, 'y': 2})
#     app.logger.info(r.backend)
#     print(r.backend)
#     return r.id
#
#
# @app.route('/simple_task_status/<task_id>')
# def get_status(task_id):
#     status = simple_app.AsyncResult(task_id, app=simple_app)
#     print("Invoking Method ")
#     return "Status of the Task " + str(status.state)
#
#
# @app.route('/simple_task_result/<task_id>')
# def task_result(task_id):
#     result = simple_app.AsyncResult(task_id).result
#     return "Result of the Task " + str(result)




###############################   Bluprint specific  ####################################################

employee_blueprint = Blueprint('employee_blueprint', __name__)
department_blueprint = Blueprint('department_blueprint', __name__)
job_title_blueprint = Blueprint('job_title_blueprint', __name__)
leave_blueprint = Blueprint('leave_blueprint', __name__)
attendance_blueprint = Blueprint('attendance_blueprint', __name__)

@employee_blueprint.route('/get_emp/',methods=['POST'])
def emp_register():
    data = request.get_json()
    email= data.get('email')
    password = data.get('password')

    # checking for existing user
    user = Employee.query.filter_by(email=email).first()
    if email.startswith('admin'):
        is_admin = True

    if not user:
        is_admin = False
        if email.startswith('admin'):
            is_admin = True
        user = Employee(
            id=data["id"], username=data["username"],
            password=generate_password_hash(data["password"]), email=data["email"],
            first_name=data["first_name"], last_name=data["last_name"], gender=data["gender"],
            age=data["age"], is_admin_status = is_admin, contact_no=data["contact_no"])


        db.session.add(user)
        db.session.commit()
        logging.info("Emp added successfully")
        return json.dumps({"SUCCESS": f"Record ({user.id}) Added Successfully...! 200"})
    else:
        return json.dumps({"ERROR": "Required fields not present"})


#
@employee_blueprint.route('/emp_login/', methods=['GET', 'POST'])
def emp_login():
    """ LOGIN WITH USER NAME AND PASSWORD AND IT RETURNS BEARER ACCESS TOKEN"""

    data = request.get_json()  # will retrive that json
    if data:
        if data.get('id') and data.get('username') and data.get('password'):
            username = data.get('username')
            password = data.get('password')
            user = Employee.query.filter_by(username=username).first()
            print("sss", user)
            if check_password_hash(user.password, data.get('password')):
                print("password")
                token = create_access_token(identity=user.username)
                print("token", token)
                logging.info("Get token when login")
                return json.dumps({"token": token})

        else:
            return json.dumps({"ERROR": "Invalid name or password"})



@employee_blueprint.route('/get_emp/', methods = ['GET'])
@jwt_required()
@simple_app.task
def get_emp_all():
    """  Get List of emp  """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    if redis_cache.exists(EMP_LIST):
        print("Getting Employee Data from redis Cache")
        emp = redis_cache.get(EMP_LIST)
        emp = literal_eval(emp.decode('utf8'))
        print("redis")
        logging.info("Get all emp")
        return jsonify({'employees': emp})
    else:
        print("Getting emp Data from mysql")
        emp = Employee.query.all()
        emps = employees_schema.dump(emp)
        emps = str(emps)
        redis_cache.set(EMP_LIST, emps)
        print("emps cache set")
        time.sleep(25)
        logging.info("Employee : %s", emps)
        return jsonify({'employees': emps})


@employee_blueprint.route('/emp/<int:id>', methods=['GET'])
@jwt_required()
def get_emp(id):
    """ GET emp POST USING ID"""
    if redis_cache.exists(EMP_LIST):
        print("Getting Employee Data from redis Cache")
        emp = redis_cache.get(EMP_LIST)
        emp = literal_eval(emp.decode('utf8'))
        print("redis")
        logging.info("Get all emp")
        return jsonify({'employees': emp})
    else:
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
            redis_cache.set(EMP_LIST, json_dict)
            print("emps cache set")
            logging.info("Get Employee with particular id")
            return json.dumps(json_dict, indent=4, sort_keys=True, default=str)
        else:
            return json.dumps({"ERROR": f"No Employee with Given Id {id}"})


@employee_blueprint.route('/emp/<int:id>', methods=['PUT'])
@jwt_required()
def update_emp(id):
    """ UPDATE Department POST"""

    emp = Employee.query.filter_by(id=id).first()
    if emp:
        data = request.get_json()
        if data:
            if data.get('username') and data.get('password') and data.get('email') and data.get(
                    'first_name') and data.get('last_name') and data.get('gender') and data.get('age') and data.get(
                    'contact_no'):
                emp.username = data.get('username')
                emp.password = data.get('password')
                emp.email = data.get('email')
                emp.first_name = data.get('first_name')
                emp.last_name = data.get('last_name')
                emp.gender = data.get('gender')
                emp.age = data.get('age')
                emp.contact_no = data.get('contact_no')
                db.session.commit()
                logging.info("Employee updated successfully")
                return json.dumps({"SUCCESS": f"Record ({emp.id}) Updated Successfully...!  200"})
        return json.dumps({"ERROR": "Required fields not present"})
    return json.dumps({"ERROR": "emp with given id not present so cannot update.."})


@employee_blueprint.route('/emp/search/', methods=['POST'])
@jwt_required()
# @cache.cached(timeout=30)
def search_emp():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    if redis_cache.exists(EMP_LIST):
        print("Getting Employee Data from redis Cache")
        emp = redis_cache.get(EMP_LIST)
        emp = literal_eval(emp.decode('utf8'))
        print("redis")
        logging.info("Get all emp")
        return jsonify({'employees': emp})
    else:
        data = request.get_json()
        if data.get('username'):
            search_username = data.get('username')
            emp = Employee.query.filter_by(username=search_username).all()

        if data.get('email'):
            search_email = data.get('email')
            emp = Employee.query.filter_by(email=search_email).all()

        if not emp:
            return json.dumps({"ERROR": "Employee not present"})
        redis_cache.set(EMP_LIST, emp)
        print("emps cache set")
        return employees_schema.dump(emp)


@employee_blueprint.route('/emp/<email>', methods=['DELETE'])
@jwt_required()
def delete_emp(email):
    """ DELETE emp POST """

    emp = Employee.query.filter_by(email=email).first()
    if emp.is_admin_status==True:
        db.session.delete(emp)
        db.session.commit()
        logging.info("Employee deleted successfully")
        return json.dumps({"SUCCESS": f"Record ({email}) Removed Successfully...! 200"})
    return json.dumps({"ERROR": "Employee with given email not present so cannot Delete.."})



@attendance_blueprint.route('/view_attend/<int:id>', methods=['GET'])
@jwt_required()
def view_attendance(id):
    """Get List of attendances of particular employee"""
    current_user = get_jwt_identity()
    print("current user", current_user)
    access_token = create_access_token(identity=current_user)

    role = Attendance.query.filter_by(employee_id=id).all()
    leave = Leave.query.filter_by(employee_id=id).all()
    # print("attendance",role.__dict__)
    # print("leave",leave.__dict__)
    for i in role:
        for j in leave:
            if i.date == j.leave_date:

                if i.status == "leave" and i.total_task == "0":
                    i.status = "leave"
                    db.session.commit()

        if i.total_task < 9:
            if not i.total_task == 0:
                i.status = "half day"

        born = datetime.datetime.strptime(str(i.date), '%Y-%m-%d %H:%M:%S').weekday()
        if calendar.day_name[born] == "Saturday" or calendar.day_name[born] == "Sunday":
            i.status = "weekend"

        db.session.commit()
    return attendances_schema.dump(role)

@attendance_blueprint.route('/view_salary/<int:id>', methods=['GET'])
@jwt_required()
def view_salary(id):
    """Get List of attendances of particular employee"""
    current_user = get_jwt_identity()
    print("current user", current_user)
    access_token = create_access_token(identity=current_user)
    sal = Job_title.query.filter_by(id=id).first()
    if sal:
        json_dict = {"job_ID": sal.id,
                     "job_title": sal.job_title,
                     "salary": sal.salary

                     }
        logging.info("Get Salary of {current_user}")
        return json.dumps(json_dict, indent=4, sort_keys=True, default=str)
    else:
        return json.dumps({"ERROR": f"salary not assign to  {current_user}"})



# ##########################    DEPARTMENT START HERE     #############################################

@department_blueprint.route('/get_dept/', methods=['POST'])
@jwt_required()
def add_dept():
    """ ADD dept WITH BEARER TOKEN"""

    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    data = request.get_json()
    if data:
        if data.get('id'):
            id = data.get('id')
            dept = Department.query.filter_by(id=id).first()
            if dept:
                return json.dumps({"ERROR": "Duplicate Department -->401"})
            depart = Department(**data)
            db.session.add(depart)
            db.session.commit()
            logging.info("Department added successfully")

            return json.dumps({"SUCCESS": f"Record ({depart.id}) Added Successfully...! 200"})

        return json.dumps({"ERROR": "Required fields not present"})
    else:
        return json.dumps({"ERROR": "EMPTY BODY, ALL FIELDS REQUIRED"})


@department_blueprint.route('/dept/<int:id>', methods=['GET'])
@jwt_required()
def get_dept(id):
    """ GET dept POST USING ID"""
    current_user = get_jwt_identity()
    print("current user",current_user)
    access_token = create_access_token(identity=current_user)
    dept = Department.query.filter_by(id=id).first()
    if dept:
        json_dict = {"Department_ID": dept.id,
                     "Department_name": dept.name,

                     }
        logging.info("Get Department with particular id")
        return json.dumps(json_dict, indent=4, sort_keys=True, default=str)
    else:
        return json.dumps({"ERROR": f"No Department with Given Id {id}"})


@department_blueprint.route('/get_all_dept/', methods=['GET'])
@jwt_required()
def get_all_dept():
    """Get List of Department"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    if redis_cache.exists(DEPART_LIST):
        print("Getting Dept Data from redis Cache")
        dept = redis_cache.get(DEPART_LIST)
        dept = literal_eval(dept.decode('utf8'))
        print("redis")
        logging.info("Get all dept")
        return jsonify({'Department': dept})
    else:
        print("Getting emp Data from mysql")
        all_dept = Department.query.all()
        dept = departments_schema.dump(all_dept)
        depts = str(dept)
        redis_cache.set(DEPART_LIST, depts)
        print("dept cache set")
        logging.info("Department : %s", depts)
        return jsonify({'Department': depts})


@department_blueprint.route('/dept/<int:id>', methods=['PUT'])
@jwt_required()
def update_dept(id):
    """ UPDATE Department POST"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    dept = Department.query.filter_by(id=id).first()
    if dept:
        data = request.get_json()
        if data:
            if data.get('name'):
                dept.name = data.get('name')

                db.session.commit()
                logging.info("Department updated successfully")
                return json.dumps({"SUCCESS": f"Record ({dept.id}) Updated Successfully...!  200"})
        return json.dumps({"ERROR": "Required fields not present"})
    return json.dumps({"ERROR": "Department with given id not present so cannot update.."})


@department_blueprint.route('/dept/search/', methods=['POST'])
@jwt_required()
# @cache.cached(timeout=30)
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


@department_blueprint.route('/dept/<int:id>', methods=['DELETE'])
def delete_dept(id):
    """ DELETE BLOG POST """

    dept = Department.query.filter_by(id=id).first()
    if dept:
        db.session.delete(dept)
        db.session.commit()
        logging.info("Department deleted successfully")
        return json.dumps({"SUCCESS": f"Record ({id}) Removed Successfully...! 200"})
    return json.dumps({"ERROR": "Department with given id not present so cannot Delete.."})


# ##########################################  Job Title START HERE  ########################################################


@job_title_blueprint.route('/post_job/', methods=['POST'])
@jwt_required()
def add_job():
    """Post List of role """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    data = request.get_json()
    if data:
        if data["id"]:
            job = Job_title.query.filter_by(id=data["id"]).first()
            if job:
                return json.dumps({"ERROR": "employee with Duplicate job-->401"})
            rol = Job_title(id=data["id"], job_title=data["job_title"], salary=data["salary"],
                            department_id=data["department_id"], employee_id=data["employee_id"])
            db.session.add(rol)
            db.session.commit()
            logging.info("Job added successfully")
            return json.dumps({"SUCCESS": f"Record ({rol.id}) Added Successfully...!  200"})
        return json.dumps({"ERROR": "Required fields not present"})
    else:
        return json.dumps({"ERROR": "EMPTY BODY, ALL FIELDS REQUIRED"})




@leave_blueprint.route('/post_leave/', methods=['POST'])
@jwt_required()
def add_leave():
    """Post List of role """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    data = request.get_json()
    if data:
        if data["id"]:
            leave = Leave.query.filter_by(id=data["id"]).first()
            if leave:
                return json.dumps({"ERROR": "employee with already leave on this date->401"})
            leave = Leave(id=data["id"], leave_date=data["leave_date"], employee_id=data["employee_id"],
                          job_title_id=data["job_title_id"])
            db.session.add(leave)
            db.session.commit()
            logging.info("On duty time added successfully")
            return json.dumps({"SUCCESS": f"Record ({leave.id}) Added Successfully...!  200"})
        return json.dumps({"ERROR": "Required fields notleave present"})
    else:
        return json.dumps({"ERROR": "EMPTY BODY, ALL FIELDS REQUIRED"})



@attendance_blueprint.route('/post_attend/', methods=['POST'])
@jwt_required()
def add_attend():
    """Post List of role """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    data = request.get_json()
    # if data:
    # if data["id"]:
    # attend = Attendance.query.filter_by(id=data["id"]).first()
    # if attend:
    #     return json.dumps({"ERROR" : "employee with duplicate attend on this date->401"})
    attendc = Attendance(id=data["id"], total_task=data["total_task"], date=data["date"], status=data["status"],
                         employee_id=data["employee_id"], job_title_id=data["job_title_id"], leave_id=data["leave_id"])
    db.session.add(attendc)
    db.session.commit()
    logging.info("On duty time added successfully")
    return json.dumps({"SUCCESS": f"Record ({attendc.id}) Added Successfully...!  200"})


@attendance_blueprint.route('/attend_info/<int:id>', methods=['GET'])
@jwt_required()
def get_attend(id):
    """role detail view."""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    role = Attendance.query.filter_by(id=id).first()
    if role:
        json_dict = {"role_ID": role.id,
                     "role_total task": role.total_task,
                     "role_date": role.date,
                     "emp_status": role.status,
                     "role_job_title": role.job_title_id,
                     "role_employee_id": role.employee_id,
                     "role_leave_id": role.leave_id
                     }
        logging.info("Get attendance with particular id.")
        return attendance_schema.dump(role)
    else:
        return json.dumps({"ERROR": f"No attendance with Given Id {id}"})


@job_title_blueprint.route('/get_job/', methods=['GET'])
# @cache.cached(timeout=30)
@jwt_required()
def get_job_all():
    """Get List of job"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    all_job = Job_title.query.all()

    logging.info("Get all role ")
    return job_titles_schema.dump(all_job)


@leave_blueprint.route('/get_leave/', methods=['GET'])
# @cache.cached(timeout=30)
@jwt_required()
def get_leave_all():
    """Get List of job"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    if redis_cache.exists(LEAVE_LIST):
        print("Getting Leave Data from redis Cache")
        leave = redis_cache.get(LEAVE_LIST)
        leave = literal_eval(leave.decode('utf8'))
        print("redis")
        logging.info("Get all leave")
        return jsonify({'Leaves': leave})
    else:
        print("Getting emp Data from mysql")
        leave = Leave.query.all()
        leave = leaves_schema.dump(leave)
        leaves = str(leave)
        redis_cache.set(LEAVE_LIST, leaves)
        print("leave cache set")
        logging.info("Leaves : %s", leaves)
        return jsonify({'Leaves': leaves})



@attendance_blueprint.route('/get_attend/', methods=['GET'])
# @cache.cached(timeout=30)
@jwt_required()
def get_attend_all():
    """Get List of job"""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    allattend = Attendance.query.all()

    logging.info("Get all role ")
    return attendances_schema.dump(allattend)
