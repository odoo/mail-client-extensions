# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""INSERT INTO account_chart_template (name, code_digits)
        values ('migration_chart_9_0_1_1', 1)
        RETURNING id""")

    id = cr.fetchone()

    util.create_column(cr, 'res_company', 'chart_template_id', 'int4')

    cr.execute("""UPDATE res_company
        SET chart_template_id = %s
        """, (id,))
