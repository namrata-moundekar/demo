from migrate_cmd import db
from datetime import datetime
from marshmallow import Schema, fields
from flask_marshmallow import Marshmallow

class Attendance(db.Model):
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    total_task = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    status = db.Column(db.String(60))
    job_title_id = db.Column(db.Integer, db.ForeignKey('job_titles.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    leave_id = db.Column(db.Integer, db.ForeignKey('leaves.id'))


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


class Leave(db.Model):
    __tablename__ = 'leaves'

    id = db.Column(db.Integer, primary_key=True)
    leave_date = db.Column(db.DateTime)
    job_title_id = db.Column(db.Integer, db.ForeignKey('job_titles.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    attendances = db.relationship('Attendance', backref='leave',
                                  lazy='dynamic')


class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False, unique=True)
    password = db.Column(db.String(130), nullable=True)
    email = db.Column(db.String(60), unique=True)
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))
    gender = db.Column(db.String(60))
    age = db.Column(db.Integer)
    is_admin_status = db.Column(db.Boolean, default=False)
    contact_no = db.Column(db.String(60))
    job_titles = db.relationship('Job_title', backref='employee',
                                 lazy='dynamic')
    leaves = db.relationship('Leave', backref='employee',
                             lazy='dynamic')
    attendances = db.relationship('Attendance', backref='employee',
                                  lazy='dynamic')


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    job_titles = db.relationship('Job_title', backref='department',
                                 lazy='dynamic')


class AttendanceSchema(Schema):
    class Meta:
        model = Attendance
        load_instance = True
        include_relationships = True
        fields = ("id", "total_task", "date", "status", "employee_id")


class LeaveSchema(Schema):
    class Meta:
        model = Leave
        load_instance = True
        include_relationships = True
        fields = ("id", "leave_date", "job_title_id", "employee_id", "attendances")

    attendances = fields.Nested(AttendanceSchema, many=True)


class Job_titleSchema(Schema):
    class Meta:
        model = Job_title
        load_instance = True
        include_relationships = True
        fields = ("id", "job_title", "salary", "department_id", "employee_id", "leaves")

    leaves = fields.Nested(LeaveSchema, many=True)


class DepartmentSchema(Schema):
    class Meta:
        model = Department
        load_instance = True
        include_relationships = True
        fields = ("id", "name", "job_titles")

    job_titles = fields.Nested(Job_titleSchema, many=True)


class EmployeeSchema(Schema):
    class Meta:
        model = Employee
        load_instance = True
        include_relationships = True
        fields = (
        "id", "username", "password", "email", "first_name", "last_name", "is_admin_status", "gender", "age", "contact_no", "job_titles")

    job_titles = fields.Nested(Job_titleSchema, many=True)
    # on_duties = ma.Nested(On_dutySchema, many=True)


attendance_schema = AttendanceSchema()
attendances_schema = AttendanceSchema(many=True)

leave_schema = LeaveSchema()
leaves_schema = LeaveSchema(many=True)

job_title_schema = Job_titleSchema()
job_titles_schema = Job_titleSchema(many=True)

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

department_schema = DepartmentSchema()
departments_schema = DepartmentSchema(many=True)


