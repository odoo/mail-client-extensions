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

    # force deletion of parent_id field.
    # For some reason ORM keep it (with its "on delete cascade" constraint) which forbid cleaning
    # of existing records in l10n_* modules
    util.remove_field(cr, 'account_account_template', 'parent_id')
