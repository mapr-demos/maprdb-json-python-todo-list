from flask import render_template, url_for, redirect, g, request
from app import app
from forms import TaskForm


from mapr.ojai.ojai_query.QueryOp import QueryOp
from mapr.ojai.storage.ConnectionFactory import ConnectionFactory

connection_string = "10.10.50.31:5678?auth=basic;user=mapr;password=mapr;ssl=false;" 
connection = ConnectionFactory.get_connection(connection_str=connection_string)

# Get a store and assign it as a DocumentStore object
if connection.is_store_exists(store_path='/apps/todos'):
    todos_table = connection.get_store(store_path='/apps/todos')
    print("Table exists")
else:
    todos_table = connection.create_store(store_path='/apps/todos')
    print("Table created")

# Configure options for application queries
options = {
    'ojai.mapr.query.include-query-plan': True,
    'ojai.mapr.query.timeout-milliseconds': 1000,
    'ojai.mapr.query.result-as-document': False
    }



@app.route('/', methods = ['GET', 'POST',])
def index(id=None):
    form = TaskForm()
    if form.validate_on_submit(): 
        # Create document
        task =  {  "_id" :  form.id.data , "title": form.title.data , "status": "Open" }
        document_to_save = connection.new_document(dictionary=task)
        todos_table.insert_or_replace(doc=document_to_save)
        return redirect(url_for('index'))

    open_todos_query = {'$select': ['*'], '$orderby' : {'status':'desc'} }
    query_result = todos_table.find( open_todos_query , options=options)
    return render_template('index.html', form = form, tasks = query_result)



@app.route('/changes_status/<id>/<status>', methods = ['GET'])
def change_status(id, status):
    # Move the status to "close" for the task
    new_status = 'Close'
    if status=='Close':
        new_status = 'Open'
    doc_mutation = connection.new_mutation().set_or_replace('status', new_status )
    todos_table.update(id, doc_mutation)
    return redirect(url_for('index'))