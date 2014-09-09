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

    if util.column_exists(cr, 'ir_ui_view', 'inherit_option_id'):
        # As script are executed module by module and not version by version,
        # if we migrate for saas-4 (or lower) to 8.0 (or higher), the initialisation
        # of the column `active` (see base/8.0.1.3/pre-60-view-application.py)
        # will not be correct as all inherited views are marked to be always applied.
        cr.execute("""UPDATE ir_ui_view
                         SET mode=%s,
                             application=CASE
                                           WHEN inherit_id IS NULL
                                           THEN %s
                                           ELSE %s
                                         END,
                             inherit_id=inherit_option_id
                      WHERE inherit_option_id IS NOT NULL""",
                   ('extension', 'disabled', 'enabled'))
