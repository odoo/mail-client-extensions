# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""UPDATE ir_model_data d
                     SET noupdate=%s
                   WHERE model=%s
                     AND res_id IN (SELECT id
                                      FROM ir_ui_view
                                     WHERE type != %s)
                     AND CONCAT(module, '.', name) != %s
               """,
               (False, 'ir.ui.view', 'qweb', 'board.board_my_dash_view'))
