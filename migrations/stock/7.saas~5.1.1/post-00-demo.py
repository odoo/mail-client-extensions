# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("SELECT demo FROM ir_module_module WHERE name='base'")
    demo = cr.fetchone()[0]
    if not demo:
        return

    cr.execute("UPDATE stock_warehouse SET in_type_id=NULL, out_type_id=NULL")
