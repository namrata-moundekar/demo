from flask import Flask, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow, fields
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint
from migrate_cmd import db
from migrate_cmd import migrate
from migrate_cmd import redis_cache
from apps import employee_blueprint, department_blueprint, job_title_blueprint, leave_blueprint, attendance_blueprint




#######################    APP CONFIG HERE  ########################################
"""      app config here    """

app = Flask(__name__, template_folder='./swagger/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Namrata.31@localhost:3306/emp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

######################    Caching CONFIG HERE  ########################################
"""      Caching config here    """

# configure the redis
app.config["REDIS_HOST"] = "localhost"
app.config["REDIS_PASSWORD"] = "password"
app.config["REDIS_PORT"] = 6379

ma = Marshmallow(app)
api = Api(app)
# cache.init_app(app)
db.init_app(app)
redis_cache.init_app(app)
migrate.init_app(app, db)

app.config["JWT_SECRET_KEY"] = "TOKEN"
jwt = JWTManager(app)

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


##########################     Models  Create HERE     #####################################



@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def welcome():
    return "<h2><b>welcome to Employee Attendance Portal</h2>"








##########################################  Blueprint register routes  ################################################

app.register_blueprint(employee_blueprint)

app.register_blueprint(department_blueprint)

app.register_blueprint(job_title_blueprint)

app.register_blueprint(leave_blueprint)

app.register_blueprint(attendance_blueprint)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
