from odoo.upgrade import util

def migrate(cr, version):
    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        util.PGRegexp(r'(</?)tree([ >])'),
        r"\1list\2",
    )
    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        util.PGRegexp(r"\ytree_view_ref\y"),
        'list_view_ref',
    )
    cr.execute(r"UPDATE ir_ui_view SET type = 'list' WHERE type = 'tree'")
    cr.execute(r"UPDATE ir_act_window SET view_mode = regexp_replace(view_mode, '\ytree\y', 'list', 'g') WHERE view_mode LIKE '%tree%'")
    cr.execute(r"UPDATE ir_act_window SET context = regexp_replace(context, '\ytree_view_ref\y', 'list_view_ref', 'g') WHERE context LIKE '%tree\_view\_ref%'")
