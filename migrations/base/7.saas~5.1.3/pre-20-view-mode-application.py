# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_ui_view', 'mode', 'varchar')
    util.create_column(cr, 'ir_ui_view', 'application', 'varchar')

    cr.execute("""UPDATE ir_ui_view
                     SET mode=CASE
                                WHEN inherit_id IS NULL
                                THEN %s
                                ELSE %s
                              END,
                         application=%s
                """, ('primary', 'extension', 'always'))
