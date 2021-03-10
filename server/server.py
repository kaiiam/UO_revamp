#!/usr/bin/env python3

from flask import Flask, request, render_template, redirect

from qname_processing import qname

app = Flask(__name__)

lists = qname.load_lists(
    "qname_processing/input_mappings/UCUM/om_ucum_mapping.csv",
    "qname_processing/input_mappings/UCUM/qudt_ucum_mapping.csv",
    "qname_processing/input_mappings/UCUM/uo_ucum_mapping.csv",
    "qname_processing/input_mappings/UCUM/oboe_ucum_mapping.csv",
    "qname_processing/input_mappings/QName/qname_labels.csv"
)

@app.route("/")
@app.route("/<term_id>")
def cmi(term_id=None):
    if not term_id and request.args and "code" in request.args:
        term_id = qname.reformat_backslash(request.args["code"])
        return redirect(term_id)
    if not term_id:
        return render_template("base.html", content=None)
    reformatted = qname.reformat_backslash(term_id)
    if term_id != reformatted:
        return redirect(reformatted)
    turtle = qname.qname2(term_id, lists)
    return render_template("base.html", content=turtle)
