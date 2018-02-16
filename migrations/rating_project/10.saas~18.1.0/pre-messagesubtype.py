# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.replace_record_references(
        cr,
        ('mail.message.subtype', util.ref(cr, 'rating_project.mt_issue_rating')),
        ('mail.message.subtype', util.ref(cr, 'rating_project.mt_task_rating')),
    )
    util.replace_record_references(
        cr,
        ('mail.message.subtype', util.ref(cr, 'rating_project.mt_project_issue_rating')),
        ('mail.message.subtype', util.ref(cr, 'rating_project.mt_project_task_rating')),
    )
    util.remove_record(cr, 'rating_project.mt_issue_rating')
    util.remove_record(cr, 'rating_project.mt_project_issue_rating')
