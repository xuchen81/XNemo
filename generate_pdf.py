import os, re, json
from flask import Flask
from datetime import datetime

app = Flask(__name__)

def read_data():
    with open('./data.json') as json_file:
        json_data = json.load(json_file)
        return json_data

def write_data(data):
    with open('./resume.tex', "w+") as f:
        f.write(data)
    f.close()

LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)

def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval

def compute_time_in_double(value):
    if "present" in value.lower():
        return round(int(datetime.now().strftime("%Y"))+1, 2)

    d = datetime.strptime(value, '%Y-%m')
    return int(d.strftime("%Y")) + round(int(d.strftime("%m")) / 12.00, 2)

def compute_time_in_text(value):
    if "present" in value.lower():
        return "Present"

    d = datetime.strptime(value, '%Y-%m')
    return d.strftime("%b, %Y")

def get_sorted_keys(value):
    return sorted(value)

def create_jinja_environment():
    texenv = app.create_jinja_environment()
    texenv.block_start_string = '((*'
    texenv.block_end_string = '*))'
    texenv.variable_start_string = '<(('
    texenv.variable_end_string = '))>'
    texenv.comment_start_string = '((='
    texenv.comment_end_string = '=))'
    texenv.filters['escape_tex'] = escape_tex
    texenv.filters['compute_time_in_double'] = compute_time_in_double
    texenv.filters['get_sorted_keys'] = get_sorted_keys
    texenv.filters['compute_time_in_text'] = compute_time_in_text
    return texenv

def render():
    texenv = create_jinja_environment()
    template = texenv.get_template('template.tex')
    data = read_data()
    generated_latex_content = template.render(data=data, last_year=int(datetime.now().strftime("%Y"))+1).encode('utf-8')
    write_data(generated_latex_content)
    os.system("pdflatex resume.tex")

render()
