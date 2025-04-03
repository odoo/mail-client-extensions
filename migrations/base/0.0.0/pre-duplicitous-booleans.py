# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
            SELECT table_name, column_name
              FROM information_schema.columns
             WHERE udt_name = 'bool'
               AND table_schema = 'public'
               AND column_default IS NOT NULL
               -- And not the ones defined in `base_data.sql` (bootstrap sql)
               AND NOT ARRAY[[table_name::text, column_name::text]] <@ ARRAY[
                ['res_users', 'active'],
                ['ir_module_module', 'application'],
                ['ir_module_module', 'demo'],
                ['ir_module_module', 'web'],
                ['ir_module_module', 'auto_install'],
                ['ir_module_module', 'to_buy'],
                ['ir_module_module_dependency', 'auto_install_required'],
                ['ir_model_data', 'noupdate']
               ]
        """
    )
    for table, column in cr.fetchall():
        cr.execute(util.format_query(cr, "ALTER TABLE {} ALTER COLUMN {} DROP DEFAULT", table, column))
