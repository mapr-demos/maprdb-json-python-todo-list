# Getting started with MapR-DB JSON, Python and Flask

In this project you will learn how to use the MapR-DB JSON using Python:

* Create new tables
* Create, Read, Update and Delete documents (CRUD)

MapR Data Platform 6.1 introduced the MapR Data Access Gateway (DAG) that exposes MapR-DB JSON Tables using a lightweight protocol based on ([gRPC](https://grpc.io/) and [OJAI JSON Syntax](http://www.ojai.io/) ).

This gateway is used by the MapR DB JSON Python client.

In this article you will learn how to buid a simple "To do" Web application with [MapR Python client](https://github.com/mapr/maprdb-python-client) and [Flask](http://flask.pocoo.org/).


### Prerequisites

You system should have the following components:

* MapR Data Platform 6.1 with the Data Access Gateway
* Python 2.7 or later
* Pip


## Run your first Python/MapR-DB JSON Application

### 1- Get the project and dependencies

Clone and build the repository using the following commands:

```
$ git clone https://github.com/mapr-demos/maprdb-json-python-todo-list.git
```

Install Python dependencies for Flask and MapR-DB
```
$ pip install flask

$ pip install flask-wtf

$ pip install 

$ maprdb-python-client

$ ojai-python-api

```

Optionally you can create a `requirements` file using:
```
$ pip freeze > requirements.txt
```

### 2- Run the application

Start the application using the following command:

```
$ cd maprdb-json-python-todo-list

$ python run.py

```

The applicaton starts on port `5000`.

Open your internet browser and go to:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)


Use the simple form to:

* Create new entry
* Update the entry
* Click on the status (Open/Close) to change the status



## A quick look to the Python application code

Most of the logic is happening in the `./app/views.py` file.

### Import objects

```
from mapr.ojai.ojai_query.QueryOp import QueryOp
from mapr.ojai.storage.ConnectionFactory import ConnectionFactory
```

### Connect to MapR

The MapR Python client connects to the cluster using the gateway, the application must use a connection string that use the gateway host, port and authentication method

```
connection_string = "mapr-gateway-host:5678?auth=basic;user=mapr;password=mapr;ssl=false;" 
connection = ConnectionFactory.get_connection(connection_str=connection_string)
```

The `connection_string` is composed of:
* hostname
* port, the default port of the MapR Data Access Gateway is 5678
* the `auth` parameter describe the authentication type, in MapR 6.1 the default and only value is basic
* `user` and `password` to set the user that will be used to access the database
* `ssl` true of false. When the cluster is secured the gateway will use SSL and you have to specify additional parameter about the SSL certificate

Once you have a connection you can start to use it to work with JSON Tables

### Access a table and create it if not present

The following code check if the table exists and if it does not it create it using the `create_store` method.

```
if connection.is_store_exists(store_path='/apps/todos'):
    todos_table = connection.get_store(store_path='/apps/todos')
    print("Table exists")
else:
    todos_table = connection.create_store(store_path='/apps/todos')
    print("Table created")
```

### Using the table in the flask routes

The application has now access to the `todos_table` variable that point to the `/apps/todos` table.

You can use this table in all the routes of your application.

#### List all tasks

For example in the home page that match the `/` route you need to do a `find` query and put the result of this query into a variable that will be use by the flask templates:

```
    open_todos_query = {'$select': ['*'] }
    query_result = todos_table.find( open_todos_query , options=options)
    return render_template('index.html', form = form, tasks = query_result)

```

* `open_todos_query` is a dictionnary that define the OJAI query to use to find the taks. In this specific example you just takes all the fields. You can change the query and add any of the OJAI attributes like `$where`, `$limit`, `$orderby` for example 
    * if you want to sort the tasks starting with the opened ones:  `open_todos_query = {'$select': ['*'], '$orderby' : {'status':'desc'} } ` 
    * if you want only the opened taks you can use: `open_todos_query = {'$select': ['*'], '$where' : {'$eq' : {'status' : 'Open'} } } ` 

* Once you have the query as JSON/Dictionnary you can retrieve the document using `todos_table.find()` method
* the `query_result` is passed to to the `render_template` and printed in the index.html template.


### Create/Update a Task

The application use the `/` route to also insert/update task using the "POST" HTTP verb.

```
    if form.validate_on_submit(): 
        # Create document
        task =  {  "_id" :  form.id.data , "title": form.title.data , "status": "Open" };
        document_to_save = connection.new_document(dictionary=task)
        todos_table.insert_or_replace(doc=document_to_save)
        return redirect(url_for('index'))
```

* When the form is submitted `form.validate_on_submit()` a new task object is created using form data `form.id.data` and `form.title.data`
* Then a new OJAI document is created from this object uding the `new_document` method
* And the document is saved into the DB Using the `todos_table.insert_or_replace`. In this case if the document already exist with this `_id` it is simply replaced.

### Change the status of the task

The last interaction this simple application is to change the status of a Task from Open to Close (or Close to Open) when the user clicks on the status.

For this the `@app.route('/changes_status/<id>/<status>', methods = ['GET'])` has been created.

```
@app.route('/changes_status/<id>/<status>', methods = ['GET'])
def change_status(id, status):
    # Move the status to "close" for the task
    new_status = 'Close'
    if status=='Close':
        new_status = 'Open'
    doc_mutation = connection.new_mutation().set_or_replace('status', new_status )
    todos_table.update(id, doc_mutation)
    return redirect(url_for('index'))
```

* The route contains the Id `<id>` of the document and current status of the task `<status>`
* Then you have to create a "mutation" to set the status in the JSON document to the new status `connection.new_mutation().set_or_replace('status', new_status )`
* Then you use the mutation object in the `todos_table.update(id, doc_mutation)` with the Id of the document to update

This last operation allows your application to only change the mutated fields (on the network and on disk), this means it is really efficient even when the document that is stored is a big one.


## Next Steps

This application is a very basic application that allows you to discover the MapR-DB JSON Python client, and how it could be used in a Flask Web application.

You can add many other features to the application to make it richer such as:

* Authentication
* To do by user
* Creating categories
* Date/Due Data management
* Comments
* Delete tasks
* and many more...

The methods that you will be using in a more complex application will be the same as the one that have been describe during this simple tutorial