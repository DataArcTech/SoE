from flask import Flask, render_template, request, jsonify, Response
import json
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from crypto.parallel_encryption import encryption_pipeline, decryption_pipeline
from crypto.utils import jdump
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
tasks = {}

@app.route('/')
def index():
    return "Home"

@app.route('/my-link/')
def my_link():
    print('I got clicked!')
    return 'Click.'

@app.route('/get-user/<user_id>')
def get_user(user_id):
    user_data = {
        "user_id": user_id,
        "name": "Honghao",
        "email": "xxx@gmail.com"
    }
    extra = request.args.get("extra")
    if extra:
        user_data["extra"] = extra
    return jsonify(user_data), 200

def encrypt_pii(task_id, path, names, lang, entities, parallel=None, content=None, key=None):
    status = 'COMPLETED'
    try:
        # encryption
        result = encryption_pipeline(path, names, lang, entities, False, None, key=key, tasks=tasks, task_id=task_id)
    except Exception as e:
        status = str(e)
        result = [f'Error: {e}']
    # save results to file
    encrypted_names = [] 
    for content,name in zip(result, names):
        with open(f'path/data/encryption/encrypt_{name}', 'w') as f:
            # f.write(content)
            for c in content:
                f.write(c + "\n")
            # jdump(content,f)
        encrypted_names.append('encrypt_'+name)
    tasks[task_id]['status'] = status
    tasks[task_id]['progress'] = 1
    tasks[task_id]['file_name'] = encrypted_names
    tasks[task_id]['path'] = 'path/data/encryption/'
    if len(encrypted_names) == 1:
        tasks[task_id]['path'] = tasks[task_id]['path'] + encrypted_names[0]



@app.route('/encrypt', methods=['POST'])
def encrypt_data():
    data = request.get_json()
    path = data.get('article_path')
    names = data.get('article_names')
    lang = data.get('lang')
    entities = data.get('entities')
    key = data.get('key')
    
    task_id = str(len(tasks) + 1)
    tasks[task_id] = {'status': 'PENDING', 'progress':0, 'file_name': None, 'path': None}
    # result = encryption_pipeline(path, [names], lang, entities, False, None, key=key)
    try:
        if not names:
            name = path.split('/')[-1]
            path = path[:-len(name)]
            names = [name]
            print(path)
            print(names)
    except Exception as e:
        tasks[task_id]['status'] = 'Error: path error.'
    # Start the task asynchronously
    # Create a unique task ID and initialize task status
    


    # Run the task in a background thread
    threading.Thread(target=encrypt_pii, args=(task_id, path, names, lang, entities, False, None, key)).start()

    return jsonify({"task_id": task_id, "status_url": f"/task-status/{task_id}"}), 202

def decrypt_pii(task_id, path, names, lang, parallel=None, content=None, key=None):
    status = 'COMPLETED'
    try:
        result = decryption_pipeline(path, names, lang, False, None, key=key, tasks=tasks, task_id=task_id)
    except Exception as e:
        status = str(e)
    decrypted_names = [] 
    for content,name in zip(result, names):
        with open(f'path/data/decryption/decrypt_{name}', 'w') as f:
            # f.write(content)
            for c in content:
                f.write(c + "\n")
            # jdump(content,f)
        decrypted_names.append('decrypt_'+name)
    tasks[task_id]['status'] = status
    tasks[task_id]['progress'] = 1
    tasks[task_id]['file_name'] = decrypted_names
    tasks[task_id]['path'] = 'path/data/decryption/'
    if len(decrypted_names) == 1:
        tasks[task_id]['path'] = tasks[task_id]['path'] + decrypted_names[0]

@app.route('/decrypt', methods=['POST'])
def decrypt_data():
    data = request.get_json()
    path = data.get('article_path')
    names = data.get('article_names')
    lang = data.get('lang')
    # entities = data.get('entities')
    key = data.get('key')
    try:
        if not names:
            name = path.split('/')[-1]
            path = path[:-len(name)]
            names = [name]
            print(path)
            print(names)
    except Exception as e:
        tasks[task_id]['status'] = 'Error: path error.'
    # print(entities, names)
    # Start the task asynchronously
    # Create a unique task ID and initialize task status
    task_id = str(len(tasks) + 1)
    tasks[task_id] = {'status': 'PENDING', 'progress':0, 'file_name': None, 'path': None}

    # Run the task in a background thread
    threading.Thread(target=decrypt_pii, args=(task_id, path, names, lang, False, None, key)).start()

    return jsonify({"task_id": task_id, "status_url": f"/task-status/{task_id}"}), 202

@app.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    """Get the status of a specific task."""
    task = tasks.get(task_id)
    if task:
        data = {"task_id": task_id, "status": task['status'],  'progress': task['progress'], "file_name": task['file_name'], "path": task['path']}
        response = Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        return response
        # return jsonify({"task_id": task_id, "status": task['status'], "result": task['result']})
    else:
        return jsonify({"error": "Task not found"}), 404

@app.route('/create-user/', methods=["POST"])
def create_user():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        return jsonify(data), 201
    else:
        return 202



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)