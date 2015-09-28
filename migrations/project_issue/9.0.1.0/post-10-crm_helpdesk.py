# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def gen_case(cr, column, d, default=None):
    def to_sql(x):
        return cr.mogrify('%s', [x])
    if default is None:
        default = 'NULL'
    else:
        default = to_sql(default)

    case = ['WHEN {c}={k} THEN {v}'.format(c=column, k=to_sql(k), v=v) for k, v in d.items()]
    return 'CASE ' + ' '.join(case) + ' ELSE ' + default + ' END'

def migrate(cr, version):
    pre = util.import_script('base/9.0.1.3/pre-10-crm_helpdesk.py')
    if not pre.is_helpdesk_used(cr):
        return

    env = util.env(cr)
    project = env['project.project'].create({'name': 'Helpdesk'})    # XXX translation?

    def create_stage(name, seq, fold):
        return env['project.task.type'].create({
            'name': name,
            'sequence': seq,
            'project_ids': [(6, 0, [project.id])],
            'fold': fold,
        }).id

    states = [
        ('draft', 'New', False),
        ('open', 'In Progress', False),
        ('pending', 'Pending', False),
        ('done', 'Closed', True),
        ('cancel', 'Cancelled', True)
    ]
    stages = {k: create_stage(n, i, f) for i, (k, n, f) in enumerate(states)}
    stages_case = gen_case(cr, 'state', stages)

    util.create_column(cr, 'project_issue', '_tmp', 'int4')

    cr.execute("SELECT latest_version FROM ir_module_module WHERE name='crm_helpdesk'")
    [helpdesk_version] = cr.fetchone()
    team_col = 'team_id' if 'saas~6' in helpdesk_version else 'section_id'

    cols = ', '.join('''\
        create_date create_uid write_date write_uid name active date_deadline partner_id
        user_id company_id description date_closed date email_cc email_from priority duration
    '''.split())

    cr.execute("""
        INSERT INTO project_issue(_tmp, project_id, kanban_state, {cols}, team_id, stage_id, channel)
        SELECT id, {project}, 'normal', {cols}, {team_col}, {stages},
               (SELECT name FROM utm_medium WHERE id=h.channel_id)
          FROM crm_helpdesk h
    """.format(cols=cols, team_col=team_col, stages=stages_case, project=project.id))

    cr.execute("""
        INSERT INTO project_tags(name)
             SELECT c.name
               FROM crm_helpdesk h JOIN crm_helpdesk_category c ON (c.id = h.categ_id)
              WHERE NOT EXISTS(SELECT 1 FROM project_tags WHERE name=c.name)
           GROUP BY c.name
    """)
    cr.execute("""
        INSERT INTO project_issue_project_tags_rel(project_issue_id, project_tags_id)
             SELECT i.id, t.id
               FROM project_issue i
               JOIN crm_helpdesk h ON (i._tmp = h.id)
               JOIN crm_helpdesk_category c ON (c.id = h.categ_id)
               JOIN project_tags t ON (t.name = c.name)
    """)

    util.remove_column(cr, 'project_issue', '_tmp')
    util.delete_model(cr, 'crm.helpdesk')
    util.delete_model(cr, 'crm.helpdesk.category')
    util.remove_module(cr, 'crm_helpdesk')
