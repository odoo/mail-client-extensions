# -*- coding: utf-8 -*-
from __future__ import division
from math import ceil
import json
import os
import odoo
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'project_issue'):
        return

    env = util.env(cr)
    Projects = env['project.project']

    nosplit = os.environ.get('ODOO_MIG_S18_NOSPLIT_PROJECTS', '')
    if nosplit:
        project_filter = 'AND p.id NOT IN %s'
        params = [tuple(int(s) for s in nosplit.split(','))]
    else:
        project_filter, params = '', []

    cr.execute("""
        SELECT p.id, p.label_issues
          FROM project_project p
         WHERE EXISTS(SELECT 1 FROM project_task WHERE project_id = p.id)
           AND EXISTS(SELECT 1 FROM project_issue WHERE project_id = p.id)
           {0}
    """.format(project_filter), params)
    for pid, label in cr.fetchall():
        project = Projects.browse(pid)
        name = u'%s (%s)' % (project.name, label)
        code = (u'%s (%s)' % (project.code, label)) if project.code else False
        nid = project.copy({
            'name': name,
            'code': code,
            'tasks': False,
            'label_tasks': label,
        }).id
        cr.execute("UPDATE project_issue SET project_id=%s WHERE project_id=%s", [nid, pid])

    # create a new field to store the old issue id.
    # can be usefull if issue id was used a reference for customers
    # stored as `varchar` to avoid formating in UI.
    util.create_column(cr, 'project_task', 'x_original_issue_id', 'varchar')
    IMF = env['ir.model.fields']
    # do not call IMF.create() to avoid reloading the registry
    odoo.models.Model.create(IMF, {
        'name': 'x_original_issue_id',
        'ttype': 'char',
        'model': 'project.task',
        'model_id': env['ir.model']._get_id('project.task'),
        'field_description': 'Legacy Reference',
        'readonly': True,
        'index': True,
        'state': 'manual',
    })
    IMF.clear_caches()

    ignore = ('id', 'description')
    cols = set(util.get_columns(cr, 'project_task', ignore)[0]) \
         & set(util.get_columns(cr, 'project_issue', ignore)[0])    # noqa:E127

    cr.execute("""
        INSERT INTO project_task(x_original_issue_id, description, {0})
        SELECT id, CONCAT('<pre>', description, '</pre>'), {0}
          FROM project_issue i
        RETURNING x_original_issue_id::integer, id
    """.format(','.join(cols)))

    cs = 1024
    sz = ceil(cr.rowcount / cs)
    for issues in util.log_progress(util.chunks(cr.fetchall(), cs, fmt=dict), qualifier='issue buckets', size=sz):
        util.replace_record_references_batch(cr, issues, 'project.issue', 'project.task')
        cr.execute("""
            INSERT INTO project_tags_project_task_rel(project_tags_id, project_task_id)
                 SELECT project_tags_id, ('{}'::json->>project_issue_id::varchar)::int4
                   FROM project_issue_project_tags_rel
                  WHERE project_issue_id IN %s
        """.format(json.dumps(issues)), [tuple(issues)])

    cr.execute("SELECT GREATEST(nextval('project_task_id_seq'), nextval('project_issue_id_seq'))")
    cr.execute("ALTER SEQUENCE project_task_id_seq RESTART WITH %s", cr.fetchone())
    cr.execute("UPDATE project_task SET priority='1' WHERE priority='2'")

    for mt in 'new blocked ready stage'.split():
        util.replace_record_references(
            cr,
            ('mail.message.subtype', util.ref(cr, 'project.mt_issue_' + mt)),
            ('mail.message.subtype', util.ref(cr, 'project.mt_task_' + mt)),
        )
        util.replace_record_references(
            cr,
            ('mail.message.subtype', util.ref(cr, 'project.mt_project_issue_' + mt)),
            ('mail.message.subtype', util.ref(cr, 'project.mt_project_task_' + mt)),
        )

    # as issues (tasks) have change project,
    # we need to reassign aliases and rating to the correct parent record
    cr.execute("""
        UPDATE mail_alias a
           SET alias_parent_thread_id = t.project_id
          FROM project_task t, ir_model m, ir_model p
         WHERE m.id = a.alias_model_id
           AND m.model = 'project.task'
           AND p.id = a.alias_parent_model_id
           AND p.model = 'project.project'
           AND t.id = a.alias_force_thread_id
    """)
    if util.table_exists(cr, 'rating_rating'):
        cr.execute("""
            UPDATE rating_rating r
               SET parent_res_id = t.project_id
              FROM project_task t
             WHERE r.res_model = 'project.task'
               AND r.parent_res_model = 'project.project'
               AND t.id = r.res_id
        """)

    model_issue = env['ir.model']._get_id('project.issue')
    model_task = env['ir.model']._get_id('project.task')

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

    cr.execute(
        "UPDATE mail_template SET model='project.task', model_id=%s WHERE model='project.issue'",
        [model_task]
    )

    # FIXME/TODO reassign gamification goals?

    # create inherited view to show the new field
    vid = util.env(cr)['ir.ui.view'].create({
        'model': 'project.task',
        'name': 'Show Legacy Reference',
        'inherit_id': util.ref(cr, 'project.view_task_form2'),
        'type': 'form',
        'active': False,
        'arch': """<data>
                     <field name='tag_ids' position='after'>
                       <field name='x_original_issue_id'/>
                     </field>
                   </data>""",
    }).id
    cr.execute('UPDATE ir_ui_view SET active=true WHERE id=%s', [vid])
