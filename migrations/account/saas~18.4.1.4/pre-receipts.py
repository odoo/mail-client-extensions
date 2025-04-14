from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_config_settings", "show_sale_receipts", "boolean")

    sale_receipts_group = util.ref(cr, "account.group_sale_receipts")
    user_group = util.ref(cr, "base.group_user")
    cr.execute(
        """
        SELECT hid
          FROM res_groups_implied_rel
         WHERE hid = %s
           AND gid = %s
    """,
        [sale_receipts_group, user_group],
    )

    show_sale_receipts = bool(cr.rowcount)

    env = util.env(cr)
    ICP = env["ir.config_parameter"]
    ICP.set_param("account.show_sale_receipts", show_sale_receipts)

    util.remove_field(cr, "res.config.settings", "group_show_sale_receipts")
    util.remove_field(cr, "res.config.settings", "group_show_purchase_receipts")
    util.remove_record(cr, "account.action_move_out_receipt_type")
    util.remove_record(cr, "account.action_move_in_receipt_type")
    util.remove_group(cr, "account.group_sale_receipts")
    util.remove_group(cr, "account.group_purchase_receipts")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "account.menu_action_move_out_receipt_type"),
            util.ref(cr, "account.menu_action_move_in_receipt_type"),
        ],
    )
    util.remove_view(cr, "account.view_in_invoice_receipt_tree")
