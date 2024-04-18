import time
import os
import io
import zipfile
import shutil

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app as app, send_file
)
from werkzeug.utils import secure_filename
from . import preprocess, predict, executor

bp = Blueprint('views', __name__)

@bp.route("/")
def index():
    return render_template('index.html.j2')


@bp.route("/predict", methods=['GET'])
def view_predict():
    return render_template('predict.html.j2')


@bp.route("/predict", methods=['POST'])
def submit_predict():
    errors = False
    error_msg = ""
    # get parameters from form
    sc = request.form['sc']
    fs = request.form['fs']
    model = request.form['model']
    method = int(request.form['method'])
    cutoff = float(request.form['cutoff'])

    # save files in new directory name based on user and microtime
    micro_time = time.time_ns() // 1000000
    work_folder = f"prediction_{micro_time}"
    work_dir = os.path.join(app.instance_path, work_folder)
    in_dir = os.path.join(work_dir, 'input')
    out_dir = os.path.join(work_dir, 'output')
    os.makedirs(work_dir)
    os.makedirs(in_dir)
    os.makedirs(out_dir)

    if not errors and 'chrname' in request.files:
        chrfile = request.files['chrname']
        chrfileFilename = secure_filename(chrfile.filename)
        chrfile.save(os.path.join(in_dir, chrfileFilename))
    else:
        errors = True
        error_msg = "Metadata CSV required"

    if not errors and 'inputname' in request.files:
        infile = request.files['inputname']
        infileFilename = secure_filename(infile.filename)
        infile.save(os.path.join(in_dir, infileFilename))
    else:
        errors = True
        error_msg = "Medicare Claims file required"

    # pass info off to prediction function
    predict.predict(fs, sc, model, infileFilename, chrfileFilename, cutoff, method, out_dir, in_dir)
    # TODO: generate summary statistics using patientlevel_prediction_merged_pt_chr.csv
    results = {
        'count': 12345,
        'recurrences': 678,
        'by_race': {
            "White Non-Hispanic": [12000, 600],
            "Black Non-Hispanic": [300, 78],
            "White Hispanic": [40, 0],
            "Black Hispanic": [5, 0],
            "Other": [0, 0]
        },
        'by_stage': {
            "0": [45, 0],
            "I": [300, 8],
            "II": [5000, 70],
            "III": [4000, 200],
            "IV": [3000, 400]
        },
        'by_year': {
            "2012": [3000, 150],
            "2013": [3000, 150],
            "2014": [3000, 150],
            "2015": [3000, 150],
            "2016": [345, 78]
        },
    }
    # output - summary statistics by race, stage, year of diagnosis
    return render_template('predict_result.html.j2', work_dir=work_folder, results=results)


@bp.route("/predict/<string:work_dir>", methods=['GET'])
def download_predict(work_dir):
    # work dir shouldn't contain slashes because of the flask string converter, but just in case sanitize the path to
    # prevent escape. it will remove the passed directory tree at the end of this so best to be extra safe...
    work_dir = os.path.relpath(os.path.normpath(os.path.join("/", work_dir)), "/")
    work_dir = os.path.join(app.instance_path, work_dir)
    out_dir = os.path.join(work_dir, "output")
    # zip up output files - out_dir/*.csv
    files = list(filter(lambda x: x.endswith('.csv'), os.listdir(out_dir)))

    file_obj = io.BytesIO()
    with zipfile.ZipFile(file_obj, 'w') as zip_file_handle:
        for file in files:
            zip_info = zipfile.ZipInfo(file)
            zip_info.date_time = time.localtime(time.time())[:6]
            zip_info.compress_type = zipfile.ZIP_DEFLATED
            with open(os.path.join(out_dir, file), 'rb') as read_file_handle:
                zip_file_handle.writestr(zip_info, read_file_handle.read())
    file_obj.seek(0)
    # delete the whole working directory
    shutil.rmtree(work_dir)
    return send_file(file_obj, mimetype="application/zip", download_name='predictions.zip', as_attachment=True)


@bp.route("/preprocess", methods=['GET'])
def view_preprocess():
    return render_template('preprocess.html.j2')


@bp.route("/preprocess", methods=['POST'])
def submit_preprocess():
    errors = False
    error_msg = ""
    # get parameters from form
    user = request.form['user']
    num_data = request.form['numdata']
    month_len_medicaid = int(request.form['mld'])
    month_len_medicare = int(request.form['mle'])
    start_medicaid = request.form['sd']
    start_medicare = request.form['se']
    drug_code = request.form['dc']

    # save files in new directory name based on user and microtime
    micro_time = time.time_ns() // 1000000
    job_name = f"preprocess_{user}_{micro_time}"
    work_dir = os.path.join(app.instance_path, job_name)
    in_dir = os.path.join(work_dir, 'input')
    out_dir = os.path.join(work_dir, 'output')
    os.makedirs(work_dir)
    os.makedirs(in_dir)
    os.makedirs(out_dir)

    if not errors and 'metacsv' in request.files:
        metacsv = request.files['metacsv']
        metacsvFilename = secure_filename(metacsv.filename)
        metacsv.save(os.path.join(in_dir, metacsvFilename))
    else:
        errors = True
        error_msg = "Metadata CSV required"

    if not errors and 'mecareClaims' in request.files:
        mecareClaims = request.files['mecareClaims']
        mecareClaimsFilename = secure_filename(mecareClaims.filename)
        mecareClaims.save(os.path.join(in_dir, mecareClaimsFilename))
    else:
        errors = True
        error_msg = "Medicare Claims file required"

    if not errors and 'mecareEnroll' in request.files:
        mecareEnroll = request.files['mecareEnroll']
        mecareEnrollFilename = secure_filename(mecareEnroll.filename)
        mecareEnroll.save(os.path.join(in_dir, mecareEnrollFilename))
    else:
        errors = True
        error_msg = "Medicare Enrollment file required"

    if not errors and 'mecaidClaims' in request.files:
        mecaidClaims = request.files['mecaidClaims']
        mecaidClaimsFilename = secure_filename(mecaidClaims.filename)
        mecaidClaims.save(os.path.join(in_dir, mecaidClaimsFilename))
    else:
        errors = True
        error_msg = "Medicaid Claims file required"

    if not errors and 'mecaidClaims2' in request.files:
        mecaidClaims2 = request.files['mecaidClaims2']
        mecaidClaims2Filename = secure_filename(mecaidClaims2.filename)
        mecaidClaims2.save(os.path.join(in_dir, mecaidClaims2Filename))
    else:
        errors = True
        error_msg = "Medicaid Pharmacy Claims file required"

    if not errors and 'mecaidEnroll' in request.files:
        mecaidEnroll = request.files['mecaidEnroll']
        mecaidEnrollFilename = secure_filename(mecaidEnroll.filename)
        mecaidEnroll.save(os.path.join(in_dir, mecaidEnrollFilename))
    else:
        errors = True
        error_msg = "Medicaid Enrollment file required"

    # pass info off to executor
    if not errors:
        preprocess.preprocess_data.submit_stored(
            job_name, user, num_data, in_dir, out_dir, metacsvFilename, mecareClaimsFilename, mecareEnrollFilename,
            mecaidClaimsFilename, mecaidClaims2Filename, mecaidEnrollFilename, month_len_medicaid, month_len_medicare,
            start_medicaid, start_medicare, drug_code)
        flash(f"Task {job_name} started")
    else:
        flash(error_msg)

    return render_template('index.html.j2')


@bp.route('/tasks')
def view_tasks():
    task_status = []
    for task_name in executor.futures._futures.keys():
        ts = {}
        ts['task_name'] = task_name
        ts['task_status'] = executor.futures._futures[task_name]._state
        if ts['task_status'] == 'FINISHED' and executor.futures._futures[task_name].exception() is not None:
            ts['task_message'] = executor.futures._futures[task_name].exception()
            ts['task_status'] = 'ERROR'
        task_status.append(ts)
    return render_template('tasks.html.j2', task_status=task_status)


@bp.route('/tasks/<string:task_name>/download')
def download_task(task_name):
    # work dir shouldn't contain slashes because of the flask string converter, but just in case sanitize the path to
    # prevent escape. it will remove the passed directory tree at the end of this so best to be extra safe...
    work_dir = os.path.relpath(os.path.normpath(os.path.join("/", task_name)), "/")
    work_dir = os.path.join(app.instance_path, work_dir)
    out_dir = os.path.join(work_dir, "output")

    # zip up output files - out_dir/*.csv
    files = []
    for dirpath, dirnames, filenames in os.walk(out_dir):
        for file in filenames:
            if file.startswith('All_11E_') or file.startswith('8_PatientLevel_char_'):
                files.append(os.path.join(dirpath,file))

    raise ValueError("test")
    file_obj = io.BytesIO()
    with zipfile.ZipFile(file_obj, 'w') as zip_file_handle:
        for file in files:
            zip_info = zipfile.ZipInfo(file)
            zip_info.date_time = time.localtime(time.time())[:6]
            zip_info.compress_type = zipfile.ZIP_DEFLATED
            with open(os.path.join(out_dir, file), 'rb') as read_file_handle:
                zip_file_handle.writestr(zip_info, read_file_handle.read())
    file_obj.seek(0)
    # delete the whole working directory
    shutil.rmtree(work_dir)
    future = executor.futures.pop(task_name)
    return send_file(file_obj, mimetype="application/zip", download_name='preprocess.zip', as_attachment=True)


@bp.route('/tasks/<string:task_name>/cancel')
def cancel_task(task_name):
    if executor.futures._futures[task_name].cancel():
        flash(f"Task {task_name} cancelled")
    else:
        flash("Unable to cancel task")
    return view_tasks()
