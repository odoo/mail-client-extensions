# -*- coding: utf-8 -*-

def migrate(cr, version):
    """remove editor_head views. Theses views are sometimes
       marked as noupdate due to bugs in editor
    """

    cr.execute("""DELETE FROM ir_model_data
                        WHERE model=%s
                          AND module like %s
                          AND name=%s
                    RETURNING res_id
               """, ['ir.ui.view', 'website%', 'editor_head'])
    vids = tuple(v[0] for v in cr.fetchall())
    if vids:
        cr.execute("DELETE FROM ir_ui_view WHERE id IN %s", [vids])
