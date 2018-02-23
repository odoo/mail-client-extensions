# -*- coding: utf-8 -*-
from __future__ import division
import logging
from math import ceil, log10
import os
from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger('odoo.addons.base.maintenance.migrations.project.saas-18.' + __name__)

def migrate(cr, version):
    if not util.table_exists(cr, 'project_issue'):
        return

    L = _logger.debug

    env = util.env(cr)
    Projects = env['project.project']

    nosplit = os.environ.get('ODOO_MIG_S18_NOSPLIT_PROJECTS', '')
    if nosplit:
        project_filter = 'AND p.id NOT IN %s'
        params = [tuple(int(s) for s in nosplit.split(','))]
    else:
        project_filter, params = '', []

    L('copy projects with tasks AND issues')
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

    ignore = ('id', 'description')
    cols = set(util.get_columns(cr, 'project_task', ignore)[0]) \
         & set(util.get_columns(cr, 'project_issue', ignore)[0])    # noqa:E127

    pv = util.parse_version
    if pv(version) < pv('10.saas~17'):
        desc_col = util.pg_text2html('description')
    else:
        # already converted in project_issue@saas~17
        desc_col = 'description'

    cr.execute("""
        select greatest(
            (select max(id) from project_task),
            (select max(id) from project_issue),
            2   -- at least offset 10
        )
    """)
    maxid, = cr.fetchone()
    offset = 10**ceil(log10(maxid))
    util.ENVIRON['issue_offset'] = offset
    util.announce(cr, '11.0', "Issues have their id offset of %s" % offset,
                  header=None, footer=None, pluses_for_enterprise=False)

    L('convert issues to tasks (id offset %s)', offset)
    cr.execute("""
        INSERT INTO project_task(id, description, {0})
        SELECT id + %s, {1}, {0}
          FROM project_issue
    """.format(','.join(cols), desc_col), [offset])

    L('assign tags')
    cr.execute("""
        INSERT INTO project_tags_project_task_rel(project_tags_id, project_task_id)
             SELECT project_tags_id, project_issue_id + %s
               FROM project_issue_project_tags_rel
    """, [offset])

    for ir in util.indirect_references(cr, bound_only=True):
        L('update references: %r', ir)
        upd = ""
        if ir.res_model:
            upd += "{ir.res_model} = 'project.task',"
        if ir.res_model_id:
            upd += "{ir.res_model_id} = (SELECT id FROM ir_model WHERE model='project.task'),"
        upd = upd.format(ir=ir)
        whr = ir.model_filter(placeholder="'project.issue'")

        query = """
            UPDATE "{ir.table}"
               SET {upd}
                   "{ir.res_id}" = "{ir.res_id}" + %s
             WHERE {whr}
               AND COALESCE("{ir.res_id}", 0) != 0
        """.format(**locals())

        cr.execute(query, [offset])

    L('update reference fields')
    cr.execute("SELECT model, name FROM ir_model_fields WHERE ttype='reference'")
    for model, column in cr.fetchall():
        table = util.table_of_model(cr, model)
        if util.column_exists(cr, table, column):
            cr.execute("""UPDATE "{table}"
                             SET "{column}" = 'project.task,' || ((substr("{column}", 14))::integer + %s)
                           WHERE "{column}" LIKE 'project.issue,%%'
                       """.format(table=table, column=column),
                       [offset])

    L('change sequence & task priority')
    cr.execute("SELECT max(id) + 1 FROM project_task")
    cr.execute("ALTER SEQUENCE project_task_id_seq RESTART WITH %s", cr.fetchone())
    cr.execute("UPDATE project_task SET priority='1' WHERE priority='2'")

    L('change mail.message.subtype')
    subtypes = {}
    for mt in 'new blocked ready stage'.split():
        subtypes[util.ref(cr, 'project.mt_issue_' + mt)] = util.ref(cr, 'project.mt_task_' + mt)
        subtypes[util.ref(cr, 'project.mt_project_issue_' + mt)] = util.ref(cr, 'project.mt_project_task_' + mt)

    util.replace_record_references_batch(cr, subtypes, 'mail.message.subtype',
                                         replace_xmlid=False)

    L('reassign other records model')
    model_issue = env['ir.model']._get_id('project.issue')
    model_task = env['ir.model']._get_id('project.task')

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
    cr.execute("UPDATE mail_alias SET alias_model_id=%s WHERE alias_model_id=%s",
               [model_task, model_issue])

    if util.table_exists(cr, 'rating_rating'):
        cr.execute("""
            UPDATE rating_rating r
               SET parent_res_id = t.project_id
              FROM project_task t
             WHERE r.res_model = 'project.task'
               AND r.parent_res_model = 'project.project'
               AND t.id = r.res_id
        """)

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
