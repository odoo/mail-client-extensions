# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Due to a bug in `remove_module` (fixed in previous commit), databases created before `9.0`
    # already have an xmlid for the `contacts` module (deleted in 9.0, back in 9.saas~12),
    # which generate a constraint violation when we try to recreate it `new_module`
    # cleanup all the previously forgotten xmlids
    cr.execute("""
        DELETE FROM ir_model_data
              WHERE model='ir.module.module'
                AND res_id NOT IN (SELECT id FROM ir_module_module)
    """)
