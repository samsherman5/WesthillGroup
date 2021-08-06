# Required Flask Libraries

from flask import Flask, request, render_template, redirect, send_from_directory

 

from google.cloud import translate_v2 as translate

translate_client = translate.Client()

# Imports the Google Cloud client library

from google.cloud import datastore

 

# START Translate requirements

#from google.cloud import translate 

from google.cloud import translate_v2 as translate

translate_client = translate.Client()

 

client = datastore.Client()

kind = 'Custinfo'

 

# Start Flask app

app = Flask(__name__)

 

 

# Index Page retrieves all records in kind and puts them into list for navigation selection

@app.route('/', methods=['GET'])

def index():

    # Get Customer List

    # retrieves all data with Kind custinfo

    query = client.query(kind=kind)

    # fetch method that retrieve all results that match query

    results = list(query.fetch())

  

    # all data stored in simple list and list is passed thru to the index.html page

    return render_template('index.html', customers=results)

 

 

# Static directory for css

@app.route('/static/<path:path>')

def send_js(path):

    return send_from_directory('static', path)

 

 

# CRUD ENDPOINTS

# Create

@app.route('/create', methods=['POST', 'GET'])

def create():

    if request.method == 'POST':

        data = request.form.to_dict(flat=True)      # Data from form

 

        # Put customer record

        complete_key = client.key(kind, data['Name'])

        customer = datastore.Entity(key=complete_key)

        customer.update({

            'Name': data['Name'],

            'address': data['address'],

            'instructions': data['instructions'],

            'address_type': data['address_type']

        })

        client.put(customer)

 

        # Redirect to customer page

        return redirect("/read/" + data['Name'])

    else:

        # GET - Render customer creation form

        return render_template('create.html')

 

 

# Read

@app.route('/read/<name>', methods=['GET'])

def read(name):

    # Retrieve Customer Data
    key = client.key(kind, name)
    customer = client.get(key)
    tinst = customer['instructions']
    tlang = 'es'
    result = translate_client.translate(tinst, target_language=tlang)

    # Render the page

    # translate process should go here

    return render_template('customer.html', name=customer['Name'], address=customer['address'],
                           instructions=customer['instructions'], transinstructions=result['translatedText'], address_type=customer['address_type'])

# Update
@app.route('/update/<name>', methods=['GET', 'POST'])
def update(name):
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)      # Data from form

 

        # Update Customer Data
        key = client.key(kind, name)
        customer = client.get(key)
        customer['address'] = data['address']
        customer['instructions'] = data['instructions']
        customer['address_type'] = data['address_type']
        client.put(customer)
        # Redirect to customer page
        return redirect("/read/" + name)
    else:
        # Get customer data
        key = client.key(kind, name)
        customer = client.get(key)

 

        # Renders update page with existing data
        return render_template('update.html', name=customer['Name'], address=customer['address'],
                               instructions=customer['instructions'], address_type=customer['address_type'])

 

 

# Delete

@app.route('/delete/<name>', methods=['GET'])

def delete(name):
    # Delete Customer Record
    key = client.key(kind, name)
    client.delete(key)
    # Redirect to index page

    return redirect('/')

 

 

# Don't worry about this part

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)