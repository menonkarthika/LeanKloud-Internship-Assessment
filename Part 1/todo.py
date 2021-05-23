from flask import Flask, request
from flask_restx import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
import datetime
from functools import wraps
import MySQLdb

auth_types={
    'AccessKey':{
        'type':'apiKey',
        'in':'header',
        'name':'Key-Type'
    }
}

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',description='A simple TodoMVC API',authorizations=auth_types)

ns = api.namespace('todos', description='TODO operations')


#Configure db

mydb = MySQLdb.connect(host="localhost",user="root",passwd="karthika",db="flaskapp")



todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'dueby': fields.Date(required=True, description='When the task should be finished'),
    'status': fields.String(required=True, description='Status of the task')

})



class TodoDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []

    def get(self, id):
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        self.todos.append(todo)
        cur = mydb.cursor()
        query = "INSERT INTO todo(id,task,dueby,status) VALUES(%s,%s,%s,%s)"
        val= (todo['id'],todo['task'],todo['dueby'],todo['status'])
        cur.execute(query,val)
        mydb.commit()
        return todo

    def update(self, id, data):
        todo = self.get(id)
        todo.update(data)
        cur = mydb.cursor()
        sql = "UPDATE todo SET task = %s, dueby=%s, status=%s WHERE id = %s"
        val = (data['task'],data['dueby'],data['status'],id)
        cur.execute(sql, val)
        mydb.commit()
        return todo

    def updatestatus(self, id, data):
        for todo in self.todos:
            if todo['id']==id:
                todo['status']=data["status"]
        cur = mydb.cursor()
        sql = "UPDATE todo SET status=%s WHERE id = %s"
        val = (data['status'], id)
        cur.execute(sql, val)
        mydb.commit()
        return todo

    def getfinished(self):
        finished=[]
        for todo in self.todos:
            if todo['status'] == 'Finished':
                finished.append(todo)
        if(finished):
            return finished
        api.abort(404, "Todo {} doesn't exist".format(id))

    def getoverdue(self):
        overdue=[]
        for todo in self.todos:
            if datetime.datetime.strptime(todo['dueby'], '%Y-%m-%d') < datetime.datetime.today():
                overdue.append(todo)
        if (overdue):
            return overdue

        api.abort(404, "Todo {} doesn't exist".format(id))

    def getdue(self, dueby):
        due = []
        for todo in self.todos:
            print(datetime.datetime.strptime(todo['dueby'], '%Y-%m-%d'))
            print(datetime.datetime.strptime(dueby, '%Y-%m-%d'))
            if datetime.datetime.strptime(todo['dueby'], '%Y-%m-%d') == datetime.datetime.strptime(dueby, '%Y-%m-%d'):
                due.append(todo)
        if (due):
            return due

        api.abort(404, "Todo {} doesn't exist".format(id))


    def delete(self, id):
        todo = self.get(id)
        self.todos.remove(todo)
        cur = mydb.cursor()
        statmt = "DELETE FROM todo WHERE id = %s"
        cur.execute(statmt, (id,))
        mydb.commit()


DAO = TodoDAO()
cur = mydb.cursor()
sql = "DELETE FROM todo"
cur.execute(sql)
mydb.commit()
DAO.create({'task': 'Build an API','dueby': "2021-05-21",'status': 'In Progress'})
DAO.create({'task': '?????','dueby': "2021-05-22",'status': 'Not Started'})
DAO.create({'task': 'profit!','dueby': "2021-05-23",'status': 'Finished'})


def write_access(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        type=None
        if 'Key-Type' in request.headers:
            type=request.headers['Key-Type']
        if not type:
            return {'message': 'Access key missing!'}, 401
        cur=mydb.cursor()
        query="select * from accesskeys where keytype=\""+str(type)+"\""
        cur.execute(query)
        type_row=cur.fetchall()
        len=0
        for val in type_row:
            len+=1
            if(val[1]==0):
                return {'message':'User not authorized, can"t perform operation!'},401
        if len==0:
            return {'message': 'User not found!'}, 401
        return f(*args,**kwargs)
    return decorated


def read_access(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        type = None
        if 'Key-Type' in request.headers:
            type = request.headers['Key-Type']
        if not type:
            return {'message': 'Access key missing!'}, 401
        cur = mydb.cursor()
        query = "select * from accesskeys where keytype=\"" + str(type) + "\""
        cur.execute(query)
        type_row = cur.fetchall()
        len = 0
        for val in type_row:
            len += 1
        if len == 0:
            return {'message': 'User not found!'}, 401
        return f(*args,**kwargs)
    return decorated

@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''

    @ns.doc('list_todos', security='AccessKey')
    @read_access
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return DAO.todos

    @ns.doc('create_todo', security='AccessKey')
    @write_access
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''

        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''

    @ns.doc('get_todo', security='AccessKey')
    @read_access
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo', security="AccessKey")
    @write_access
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.doc('update_todo', security="AccessKey")
    @write_access
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id ):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

    @ns.doc('changestatus_todo', security="AccessKey")
    @write_access
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def patch(self, id):
        '''Change status of a task given its identifier'''
        return DAO.updatestatus(id, api.payload)

@ns.route('/finished')
@ns.response(404, 'Todo not found')
class Finished(Resource):
    '''Get completed todo items'''

    @ns.doc('finished_todo', security="AccessKey")
    @read_access
    @ns.marshal_with(todo)
    def get(self):
        '''Fetch finished tasks'''
        return DAO.getfinished()


@ns.route('/overdue')
@ns.response(404, 'Todo not found')
class Overdue(Resource):
    '''Show overdue todo items'''

    @ns.doc('overdue_todo', security="AccessKey")
    @read_access
    @ns.marshal_with(todo)
    def get(self):
        '''Fetch overdue tasks'''
        return DAO.getoverdue()


@ns.route('/<string:due_date>')
@ns.response(404, 'Todo not found')
@ns.param('due_date', 'The task due date')
class Due(Resource):
    '''Show tasks on duedate'''

    @ns.doc('duedate_todo', security="AccessKey")
    @read_access
    @ns.marshal_with(todo)
    def get(self, due_date):
        '''Fetch tasks due on given date'''
        return DAO.getdue(due_date)





if __name__ == '__main__':
    app.run(debug=True)