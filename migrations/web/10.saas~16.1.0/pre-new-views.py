# -*- coding: utf-8 -*-

def migrate(cr, version):
    renames = {
        'kanban_label_selection': 'label_selection',
        'o_form_field': 'o_field_widget',
        'o_form_input': 'o_input',
        'o_form_invisible': 'o_invisible_modifier',
    }

    for old, new in renames.items():
        cr.execute("""
            UPDATE ir_ui_view
               SET arch_db = regexp_replace(arch_db, '\y{old}\y', '{new}')
             WHERE arch_db ~ '\y{old}\y'       -- avoid updating all views
        """.format(old=old, new=new))
