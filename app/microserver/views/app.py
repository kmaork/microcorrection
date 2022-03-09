import os
from logging import getLogger, DEBUG
from flask import Flask, send_from_directory, jsonify, send_file, request, render_template, redirect, url_for

from .cpu import cpu
from .dbg import dbg
from .admin import admin
from ..utils import get_level, get_level_data, get_rom, get_levels_dict, allow_level, WITH_ADMIN, SECRET_KEY, \
    signed_serializer
from ..assembler import assemble, AssemblerException

app = Flask(__name__)
app.register_blueprint(cpu, url_prefix='/cpu')
app.register_blueprint(dbg, url_prefix='/cpu/dbg')
if WITH_ADMIN:
    app.register_blueprint(admin, url_prefix='/admin')
app.secret_key = SECRET_KEY

if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
    gunicorn_logger = getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    app.logger.setLevel(DEBUG)

app.logger.info(f'Server is run with{"" if WITH_ADMIN else "out"} admin mode')


@app.route('/')
def home():
    return render_template('micro.html.jinja2')


@app.route('/level/<level>')
def allow_level_view(level: str):
    allow_level(signed_serializer.loads(level.encode()))
    return redirect(url_for('home'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


@app.route('/get_levels')
def get_levels():
    return jsonify(get_levels_dict(only_allowed=True))


@app.route('/whoami')
def whoami():
    return jsonify(name='name', level=get_level())


@app.route('/get_manual')
def get_manual():
    manual = get_level_data('manual.txt').read_text()
    return jsonify(manual=manual)


@app.route('/rom')
def download_rom():
    filename = f'{get_level()} ROM.bin'
    return send_file(get_rom(), as_attachment=True, attachment_filename=filename)


@app.route('/assembler')
def assembler():
    return render_template('assembler.html.jinja2')


@app.route('/manual.pdf')
def micro_manual():
    return send_from_directory('static', 'manual.pdf')


@app.route('/assemble', methods=['POST'])
def assemble_post():
    opcodes = ''
    error = None
    try:
        opcodes = assemble(request.get_json()['asm']).hex()
    except AssemblerException as e:
        error = e.output
    return jsonify(error=error, opcodes=opcodes)
