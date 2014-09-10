# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("SELECT 1 FROM ir_module_module WHERE name=%s AND state IN %s",
               ["theme_zen", util._INSTALLED_MODULE_STATES])
    if not cr.fetchone():
        return
    cr.execute("""SELECT 1
                    FROM ir_ui_view
                   WHERE id IN (SELECT res_id
                                  FROM ir_model_data
                                 WHERE model=%s
                                   AND module=%s
                                   AND name like %s
                               )
                     AND active
                """, ['ir.ui.view', 'theme_zen', 'theme_zen_%'])
    if cr.fetchone():
        # if any active, abort migration
        raise util.MigrationError('Cannot migrate database because module `theme_zen` is installed and active')
    cr.execute("UPDATE ir_module_module SET state=%s WHERE name=%s", ['to remove', 'theme_zen'])
