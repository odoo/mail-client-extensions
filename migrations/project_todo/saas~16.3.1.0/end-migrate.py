# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "note.note")
    util.remove_model(cr, "note.stage")
    util.remove_model(cr, "note.tag")
    util.remove_column(cr, "project_tags", "_upg_note_tag_id")
    util.remove_column(cr, "project_task_type", "_upg_note_stage_id")
    util.remove_column(cr, "project_task", "_upg_note_id")
