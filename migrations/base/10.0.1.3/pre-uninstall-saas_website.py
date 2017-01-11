# -*- coding: utf-8 -*-

def migrate(cr, version):
    # `saas_website` is obsolet since september 2016.
    # Force uninstalling it.
    cr.execute("""
        UPDATE ir_module_module
           SET state = 'to remove'
         WHERE name = 'saas_website'
           AND state IN ('installed', 'to upgrade')
    """)
