# -*- coding: utf-8 -*-

def migrate(cr, version):
    # qweb cannot have groups anymore, force update of these views as there are chances that
    # groups have been moved as node attributes.
    cr.execute("""
        WITH views AS (
            DELETE FROM ir_ui_view_group_rel r
                  USING ir_ui_view v
                  WHERE v.id = r.view_id
                    AND v.type = 'qweb'
              RETURNING v.id
        )
        UPDATE ir_model_data d
           SET noupdate=false
          FROM views
         WHERE d.model='ir.ui.view'
           AND d.res_id = views.id
    """)
