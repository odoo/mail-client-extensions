# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        SELECT value
          FROM ir_config_parameter
         WHERE key = 'migration.target_version'
    """)
    [target_version] = cr.fetchone() or [None]
    if target_version == '11.0':
        cr.execute("""\
            UPDATE ir_module_module
            SET state = 'installed'
            WHERE
              name = 'pos_blackbox_be'
              AND state = 'to upgrade'
        """)

