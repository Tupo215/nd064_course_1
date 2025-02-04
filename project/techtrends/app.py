import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys

# Set logger to handle STDOUT and STDERR
stdout_handler = sys.stdout
stderr_handler = sys.stderr
handler = [stderr_handler, stdout_handler]


# Setting up logging 
logging.basicConfig(handlers=(logging.StreamHandler(stream=handler),logging.FileHandler('app.log')), 
                    level=logging.DEBUG, 
                    format=' %(levelname)s %(name)s%(asctime)s : %(message)s' 
                    )
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info("The Index page is retrieved")
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('A non-existing article is accessed and a 404 page is returned')  
      return render_template('404.html'), 404
    else:  
        app.logger.info("Article %s retrieved!",post_id)
        return render_template('post.html', post=post)
    

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("The About Us page is retrieved")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))
       
    return render_template('create.html')
    app.logger.info("%s article is created", title) 
# Define the healthcheck
@app.route('/healthz')
def healthcheck():
    response = app.response_class(
        response = json.dumps({'result':'OK-health'}),
        status = 200,
        mimetype = 'application/json'
        )
    
    app.logger.info("Healthz request successfull")
    return response

#Define the metrics
@app.route('/metrics')
def metrics():
    response = app.response_class(
        response = json.dumps({'db_connection_count': 1,'post_count': 6}),
        status = 200,
        mimetype = 'application/json'
        )
    
    app.logger.info("Metrics request successfull")
    return response

# start the application on port 3111
if __name__ == "__main__": 
   app.run(host='0.0.0.0', port='3111')
