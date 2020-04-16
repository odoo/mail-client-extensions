# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_model(cr, 'project.task.merge.wizard')
    util.remove_view(cr, 'project.mail_template_task_merge')
    # migrations/analytic/saas~11.2.1.1/pre-migration.py
    # util.remove_field(cr, 'account.analytic.account', 'tag_ids')
    # project.project inheritS of account.analytic.account
    util.remove_field(cr, 'project.project', 'tag_ids', drop_column=False)
