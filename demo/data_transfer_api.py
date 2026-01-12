from flask import Flask, request, jsonify, send_file, Response
import urllib.parse
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TRANSFER_FOLDERS = {
    "crypto": "/data",
    "synthesis": "/data",
    "tabular": "/data/tabular",
}

# Ensure directories exist
for folder in {**TRANSFER_FOLDERS}.values():
    os.makedirs(folder, exist_ok=True)

@app.route('/upload/<task>', methods=['POST'])
def upload_file(task):
    if task not in TRANSFER_FOLDERS:
        return jsonify({"error": f"Invalid task: {task}"}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file
    upload_folder = TRANSFER_FOLDERS[task]
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    return jsonify({"message": "File uploaded successfully!", "file_path": upload_folder, "filename": file.filename})

@app.route('/download/<task>/<filename>', methods=['GET'])
def download_file(task, filename):
    if task not in TRANSFER_FOLDERS:
        return jsonify({"error": f"Invalid task: {task}"}), 400

    download_folder = TRANSFER_FOLDERS[task]
    file_path = os.path.join(download_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": f"File {filename} not found in task {task}"}), 404
    try:
        # Encode the filename for UTF-8 compatibility
        encoded_filename = urllib.parse.quote(filename)
        response = send_file(file_path, as_attachment=True)
        response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
        return response
    except Exception as e:
        return Response(f"Error: {e}", status=500)
    # return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, debug=True)