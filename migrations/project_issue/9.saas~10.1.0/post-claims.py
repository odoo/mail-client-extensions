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

def _get_matching_columns(cr, model1, model2, ignored=()):
    table1 = util.table_of_model(cr, model1)
    table2 = util.table_of_model(cr, model2)
    ignored = tuple(set(['id'] + ignored))
    cr.execute("""
         SELECT quote_ident(f.name)
           FROM ir_model_fields f
           JOIN information_schema.columns c
             ON (    c.column_name = f.name
                 and c.table_name = CASE WHEN f.model=%(model1)s THEN %(table1)s
                                         WHEN f.model=%(model2)s THEN %(table2)s
                                         ELSE NULL END
                 )
          WHERE f.model IN (%(model1)s, %(model2)s)
            AND f.name NOT IN %(ignored)s
       GROUP BY f.name, f.ttype, f.relation, f.relation_field
         HAVING count(f.id) = 2
    """, locals())
    return [c[0] for c in cr.fetchall()]

def migrate(cr, version):
    pre = util.import_script('base/9.saas~10.1.3/pre-20-crm_claim.py')
    if not pre.is_claims_used(cr):
        return

    env = util.env(cr)
    project = env['project.project'].create({
        'name': 'Claims',
        'use_tasks': False,
        'use_issues': True,
        'label_issues': 'Claims',
    })

    # TODO convert mail aliases

    util.create_column(cr, 'project_task_type', '_tmp', 'int4')
    cr.execute("""
      WITH new_stages AS (
        INSERT INTO project_task_type(_tmp, name, sequence, fold)
        SELECT id, name, sequence, false FROM crm_claim_stage
        RETURNING id, _tmp
      ),
      _link_stages AS (
        INSERT INTO project_task_type_rel(type_id, project_id)
        SELECT id, %s FROM new_stages
      )
      SELECT id, _tmp FROM new_stages
    """, [project.id])

    stages = {r[1]: r[0] for r in cr.fetchall()}
    stages_case = gen_case(cr, 'stage_id', stages)

    util.create_column(cr, 'project_issue', '_tmp', 'int4')

    cols = ','.join(_get_matching_columns(cr, 'crm.claim', 'project.issue', ignored=['description']))

    cr.execute("""
        INSERT INTO project_issue(_tmp, project_id, kanban_state, {cols}, stage_id, description)
        SELECT id, {project}, 'normal', {cols}, {stages},
               concat('Description:\n', coalesce(description, ''),
                      '\n\nAction Type: ', coalesce(type_action, ''),
                      '\n\nTrouble Responsible: ', coalesce(user_fault, ''),
                      '\n\nCause:\n', coalesce(cause, ''),
                      '\n\nResolution:\n', coalesce(resolution, ''),
                      '')
          FROM crm_claim
    """.format(cols=cols, stages=stages_case, project=project.id))

    # migrate messages and followers
    cr.execute("""
        UPDATE mail_message m
        SET model = 'project.issue',
            res_id = i.id
        FROM project_issue i
        WHERE m.res_id = i._tmp
        AND m.model='crm.claim';
    """)
    cr.execute("""
        UPDATE mail_followers f
        SET res_model = 'project.issue',
            res_id = i.id
        FROM project_issue i
        WHERE f.res_id = i._tmp
        AND f.res_model='crm.claim';
    """)

    cr.execute("""
        INSERT INTO project_tags(name)
             SELECT c.name
               FROM crm_claim h JOIN crm_claim_category c ON (c.id = h.categ_id)
              WHERE NOT EXISTS(SELECT 1 FROM project_tags WHERE name=c.name)
           GROUP BY c.name
    """)
    cr.execute("""
        INSERT INTO project_issue_project_tags_rel(project_issue_id, project_tags_id)
             SELECT i.id, t.id
               FROM project_issue i
               JOIN crm_claim h ON (i._tmp = h.id)
               JOIN crm_claim_category c ON (c.id = h.categ_id)
               JOIN project_tags t ON (t.name = c.name)
    """)

    util.remove_column(cr, 'project_task_type', '_tmp')
    util.remove_column(cr, 'project_issue', '_tmp')
    util.remove_module(cr, 'crm_claim')
