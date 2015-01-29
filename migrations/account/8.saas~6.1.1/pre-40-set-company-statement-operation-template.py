# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_statement_operation_template', 'company_id', 'int4')
    cr.execute("""UPDATE account_statement_operation_template t
                     SET company_id = u.company_id
                    FROM res_users u
                   WHERE t.create_uid = u.id
               """)
    main_id = util.ref(cr, 'base.main_company')
    if not main_id:
        cr.execute("SELECT id FROM res_company ORDER BY id LIMIT 1")
        [main_id] = cr.fetchone() or [None]

    if main_id:
        cr.execute("""UPDATE account_statement_operation_template
                         SET company_id=%s
                       WHERE company_id IS NULL
                   """, [main_id])
