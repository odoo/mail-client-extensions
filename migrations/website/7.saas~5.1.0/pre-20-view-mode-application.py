# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""UPDATE ir_ui_view
                     SET mode=%s,
                         application=CASE
                                       WHEN inherit_id IS NULL
                                       THEN %s
                                       ELSE %s
                                     END,
                         inherit_id=inherit_option_id
                  WHERE inherit_option_id IS NOT NULL""",
               ('extension', 'disabled', 'enabled'))
