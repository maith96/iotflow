import os
import shutil
import subprocess
from flask import Flask, flash, request, redirect, render_template, url_for, send_file
from werkzeug.utils import secure_filename

UPLOAD_VSA_FOLDER = '../iotflow_files/VSA/docker/apps_to_analyze'
UPLOAD_FLA_FOLDER = '../iotflow_files/FlowAnalysis/docker/apps_to_analyze'
ALLOWED_EXTENSIONS = {'apk'}

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FLA_FOLDER'] = UPLOAD_FLA_FOLDER
app.config['UPLOAD_VSA_FOLDER'] = UPLOAD_VSA_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-apk', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(request.form['analysisType'])
        analysis_type = request.form['analysisType']

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename("uploaded.apk")
            file.save(os.path.join(app.config['UPLOAD_FLA_FOLDER'], filename))
            file.save(os.path.join(app.config['UPLOAD_VSA_FOLDER'], filename))


            try:
                if (analysis_type == 'fla'):
                    subprocess.run(['/workspaces/iotflow/server_files/fla_run.sh' ], check=True, cwd='/workspaces/iotflow/server_files/')
                elif (analysis_type == 'vsa'):
                    subprocess.run(['/workspaces/iotflow/server_files/vsa_run.sh' ], check=True, cwd='/workspaces/iotflow/server_files/')
            except subprocess.CalledProcessError as e:
                return  f"Error executing Docker command: {e}"
            return redirect(url_for('index', name=filename))
        
    return render_template('upload_form.html')


@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')

if __name__ == '__main__':
    app.run()