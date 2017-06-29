import os
import json
import settings

from flask import Flask
from flask import jsonify
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

from celery import Celery
from celery import Task

from pymongo import MongoClient


app = Flask(__name__)
app.config.from_object(settings)

# For docker the mongo url is 'mongodb://<service_name>:<port>'
client = MongoClient('mongodb://mongo:27017')
db = client.test_db
collection = db.test_collection


# Celery Init
def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@app.route('/')
def hello():
    return 'Flask + Mongo + Nginx + Celery + Redis Docker example'


###############################################################################
#
#                           CELERY TEST ROUTES
#
###############################################################################


@celery.task(name='task.add')
def add(a, b):
    return a + b


@app.route('/celery')
def test(x=3, y=4):
    try:
        x = int(request.args.get('x', x))
        y = int(request.args.get('y', y))
    except:
        pass
    task = add.apply_async((x, y))
    context = {
        'task': 'x + y',
        'id': task.id,
        'x': x,
        'y': y,
    }
    return jsonify(context)


@app.route('/celery/<task_id>')
def result(task_id):
    result = add.AsyncResult(task_id).get()
    return jsonify(result)


###############################################################################
#
#                             MONGO TEST ROUTES
#
###############################################################################

@app.route('/mongo')
def mongo_get():
    query = collection.find()
    items = list(query)
    return render_template('test.html', items=items)


@app.route('/mongo/post', methods=['POST'])
def mongo_post():
    collection.insert_one({
        'title': request.form['title'],
    })
    return redirect(url_for('mongo_get'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
  
