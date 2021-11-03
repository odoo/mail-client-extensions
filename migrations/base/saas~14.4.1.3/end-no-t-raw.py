# -*- coding: utf-8 -*-


def migrate(cr, version):
    query = r"""
        WITH t_raw AS (
            SELECT v.id
              FROM ir_ui_view v
             WHERE v.type = 'qweb'
               AND v.arch_db ~ '\yt-raw\y'
               AND NOT EXISTS (
                   SELECT 1
                     FROM ir_model_data d
                     JOIN ir_module_module m ON d.module = m.name  -- ignore unexisting modules, like __export__
                    WHERE d.model = 'ir.ui.view'
                      AND d.res_id = v.id
                      AND d.noupdate IS NOT TRUE  -- false or NULL
                   )
        )
        UPDATE ir_ui_view v
           SET arch_db = regexp_replace(arch_db, '\yt-raw\y', 't-out', 'g')
          FROM t_raw t
         WHERE t.id = v.id
    """
    cr.execute(query)
