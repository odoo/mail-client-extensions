# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        r"""
            UPDATE ir_module_module
               SET state = 'uninstallable'
             WHERE name LIKE 'hw\_%'
               AND author = 'Odoo S.A.'
        """
    )
