# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'res_partner', 'implemented_count', 'int4')
    cr.execute("""
        WITH implementors AS (
            SELECT assigned_partner_id as id, count(*) as count
              FROM res_partner
             WHERE assigned_partner_id IS NOT NULL
          GROUP BY assigned_partner_id
        )
        UPDATE res_partner p
           SET implemented_count = i.count
          FROM implementors i
         WHERE i.id = p.id
    """)
    cr.execute('UPDATE res_partner SET implemented_count=0 WHERE implemented_count IS NULL')

    util.create_column(cr, 'res_partner', 'grade_sequence', 'int4')
    cr.execute("""
        UPDATE res_partner p
           SET grade_sequence = g.sequence
          FROM res_partner_grade g
         WHERE g.id = p.grade_id
    """)
