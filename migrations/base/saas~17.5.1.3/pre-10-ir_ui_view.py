from odoo.upgrade import util


def migrate(cr, version):
    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        util.PGRegexp(r"(</?)tree([ >])"),
        r"\1list\2",
    )

    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        # replace: `/tree"`, `/tree'`, `/tree[`, or `/tree/`
        util.PGRegexp(r"(<xpath .*?expr=.+)/tree([\"'/\[])"),
        r"\1/list\2",
    )

    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        util.PGRegexp(r"\ytree_view_ref\y"),
        "list_view_ref",
    )
    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        util.PGRegexp(r'mode=([\'"])([a-z, ]*)tree([ ,a-z]*)\1'),
        r"mode=\1\2list\3\1",
    )
    util.change_field_selection_values(cr, "ir.ui.view", "type", {"tree": "list"})
    util.change_field_selection_values(cr, "ir.actions.act_window.view", "view_mode", {"tree": "list"})
    cr.execute(
        r"UPDATE ir_act_window SET view_mode = regexp_replace(view_mode, '\ytree\y', 'list', 'g') WHERE view_mode LIKE '%tree%'"
    )
    cr.execute(
        r"UPDATE ir_act_window SET context = regexp_replace(context, '\ytree_view_ref\y', 'list_view_ref', 'g') WHERE context LIKE '%tree\_view\_ref%'"
    )
    cr.execute("UPDATE ir_act_window SET mobile_view_mode = 'list' WHERE mobile_view_mode = 'tree'")
    cr.execute(
        r"UPDATE ir_actions SET binding_view_types = regexp_replace(binding_view_types, '\ytree\y', 'list', 'g') WHERE binding_view_types LIKE '%tree%'"
    )

    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        util.PGRegexp(r'name=(["\'])kanban-menu\1'),
        r"name=\1menu\1",
        extra_filter="t.arch_db::TEXT LIKE '%%kanban-card%%' AND t.type IN ('kanban', 'form')",
    )
    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        util.PGRegexp(r'name=(["\'])kanban-card\1'),
        r"name=\1card\1",
        extra_filter="t.type IN ('kanban', 'form')",
    )

    cr.execute(
        r"""
        UPDATE ir_act_server
           SET code = regexp_replace(
                        replace(replace(code, 'Tree', 'List'), 'TREE', 'LIST'),
                        '\ytree\y','list','g'
                    )
         WHERE id = %s;
        """,
        [util.ref(cr, "base.ir_action_activate_private_address_recycling")],
    )
