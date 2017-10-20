# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for f in 'issue_count issue_ids label_issues use_issues issue_needaction_count'.split():
        util.remove_field(cr, 'project.project', f)
    util.remove_field(cr, 'account.analytic.account', 'use_issues')
    util.remove_field(cr, 'res.partner', 'issue_count')
    util.remove_field(cr, 'account.analytic.line', 'issue_id')  # from `project_issue_sheet`

    env = util.env(cr)
    model_issue = env['ir.model']._get_id('project.issue')
    model_task = env['ir.model']._get_id('project.task')

    cr.execute("UPDATE mail_alias SET alias_model_id=%s WHERE alias_model_id=%s",
               [model_task, model_issue])

    cr.execute("""
        UPDATE ir_act_server
           SET model_id = %s,
               model_name = 'project.task'
         WHERE model_id = %s
    """, [model_task, model_issue])
    cr.execute("UPDATE ir_act_server SET binding_model_id=%s WHERE binding_model_id=%s",
               [model_task, model_issue])
    cr.execute("""
        WITH _u AS (
            UPDATE ir_act_server
               SET crud_model_id = %s
             WHERE crud_model_id = %s
         RETURNING id
        )
        UPDATE ir_server_object_lines l
           SET col1 = t.id
          FROM ir_model_fields i,
               ir_model_fields t
         WHERE server_id IN (select id FROM _u)
           AND i.id = l.col1
           AND t.model = 'project.task'
           AND t.name = i.name
    """, [model_task, model_issue])

    if util.table_exists(cr, 'mail_template'):
        cr.execute("""
            UPDATE mail_template
               SET model_id = %s
             WHERE model_id = %s
        """, [model_task, model_issue])

    # FIXME/TODO reassign gamification goals?

    util.remove_model(cr, 'project.issue')
    util.remove_model(cr, 'project.issue.report')       # from <= saas~16
