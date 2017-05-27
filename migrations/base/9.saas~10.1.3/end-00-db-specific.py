# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def _megamanhk(cr, version):
    # migrate old crm_claim tags to project_tags
    cr.execute('''
        INSERT INTO project_issue_project_tags_rel(project_issue_id,project_tags_id)
        SELECT i.id,
               t.id
        FROM project_issue i
        JOIN _tmp_claim_tag r ON i.x_claim_no = r.claim_no
        JOIN project_tags t ON t.name = r.tag_name;
        ''')
    cr.execute('''DROP TABLE _tmp_claim_tag;''')


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '16a70f1b-893a-4411-aa2a-d939171fac7d': _megamanhk,
    })
