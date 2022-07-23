from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask_wtf import FlaskForm
from wtforms import fields,validators

from .modules import Cook

import json

bp = Blueprint('toolkit', __name__, url_prefix='/toolkit')

@bp.route('/', methods=('GET',))
def index():
    return render_template('base.html')

class CookForm(FlaskForm):
    count = fields.IntegerField('目标箱数', [validators.NumberRange(1,10000,"差不多得了啊，只能输入%(min)-%(max)"),],default=200)
    skill = fields.IntegerField('熟练度', [validators.NumberRange(0,2000,"差不多得了啊，只能输入%(min)-%(max)"),],default=1000)
    tribute_skill = fields.IntegerField('纳贡熟练度', [validators.NumberRange(0,2000,"差不多得了啊，只能输入%(min)-%(max)"),],default=0)

@bp.route('/cook', methods=('GET', 'POST'))
def cook():
    form = CookForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.tribute_skill == 0:
               form.tribute_skill = skill
            data = {}
            for target in Cook.SUPPORTS:
                data[target] = Cook.boxData(target,form.count.data,form.skill.data,form.tribute_skill.data)
        else:
            redirect(url_for('toolkit.cookSubmit'))
        data = json.dumps(data, sort_keys = False, indent = 2,ensure_ascii=False)
        return render_template('cook/result.html', form=form,data=data)

    if request.method == 'GET':
        formdata = session.get('formdata', None)
        if not formdata:
            redirect(url_for('toolkit.cookSubmit'))
        if formdata:
            form = CookForm(MultiDict(formdata))
            form.validate()

    return render_template('cook/base.html', form=form)

@bp.route('/cook/submit', methods=('GET', 'POST'))
def cookSubmit():
    form = CookForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.tribute_skill == 0:
               form.tribute_skill = skill
            redirect(url_for('toolkit.cook'))

    return render_template('cook/base.html', form=form)

