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

    # remove dashboard view_mode from action windows
    # if no views of the same type remains
    cr.execute(
        """
         WITH actions AS (
          SELECT w.id
            FROM ir_act_window w
       LEFT JOIN ir_ui_view v
              ON v.model = w.res_model
             AND v.type = 'dashboard'
           WHERE w.view_mode LIKE '%dashboard%'
             AND v.id IS NULL
           )
       UPDATE ir_act_window w
          SET view_mode = ARRAY_TO_STRING(ARRAY_REMOVE(STRING_TO_ARRAY(w.view_mode, ','), 'dashboard'), ',')
         FROM actions a
        WHERE a.id = w.id
    """
    )
