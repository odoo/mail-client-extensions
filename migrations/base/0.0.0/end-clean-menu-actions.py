# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Remove broken references to window actions from menus
    cr.execute(
        """
        UPDATE ir_ui_menu
           SET action = NULL
         WHERE SPLIT_PART(action, ',', 1) = 'ir.actions.act_window'
           AND SPLIT_PART(action, ',', 2)::int NOT IN (
               SELECT id
                 FROM ir_act_window
         )
    """
    )
