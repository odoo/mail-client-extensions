from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "ir.ui.menu", "web_invisible")
    util.remove_field(cr, "ir.actions.actions", "binding_invisible")
    # explicit removal for databases without odoo/odoo#199109
    util.remove_field(cr, "ir.cron", "binding_invisible")
    util.rename_xmlid(cr, "base.state_id_pp", "base.state_id_pe", on_collision="merge")
    util.remove_field(cr, "base.module.uninstall", "module_id")
    util.rename_field(cr, "base.module.uninstall", "module_ids", "impacted_module_ids")

    util.remove_view(cr, "base.res_partner_view_form_private")

    # replace ir.filters user_id many2one by user_ids (many2many)
    util.create_m2m(cr, "ir_filters_res_users_rel", "ir_filters", "res_users")
    cr.execute("""
        INSERT INTO ir_filters_res_users_rel (ir_filters_id, res_users_id)
             SELECT id, user_id
               FROM ir_filters
              WHERE user_id IS NOT NULL
    """)
    util.rename_field(cr, "ir.filters", "user_id", "user_ids")
    util.remove_column(cr, "ir_filters", "user_ids")
    util.remove_record(cr, "base.ir_filters_delete_own_rule")
    util.remove_constraint(cr, "ir_filters", "ir_filters_name_model_uid_unique")
    cr.execute("DROP INDEX IF EXISTS ir_filters_name_model_uid_unique_action_index")
    util.rename_xmlid(cr, "l10n_fr.dom-tom", "base.dom-tom")

    util.remove_column(cr, "res_users_identitycheck", "password")

    util.remove_field(cr, "res.groups", "color")
    util.remove_field(cr, "res.groups", "category_id")
    util.remove_field(cr, "res.groups", "visible")
    util.remove_field(cr, "ir.module.category", "group_ids")
    util.remove_field(cr, "res.users", "view_show_technical_groups")
    util.remove_field(cr, "res.users", "view_visible_implied_group_ids")
    util.remove_field(cr, "res.users", "view_all_disjoint_group_ids")
    util.remove_field(cr, "res.users", "view_disjoint_group_ids")
