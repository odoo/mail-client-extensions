from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "purchase.action_purchase_batch_bills")
    util.remove_record(cr, "purchase.res_partner_view_purchase_account_buttons")
    util.remove_field(cr, "res.partner", "purchase_warn")
    util.remove_field(cr, "product.template", "purchase_line_warn")
    util.remove_view(cr, "purchase.purchase_partner_kanban_view")
    util.remove_record(cr, "purchase.mt_rfq_done")
    util.create_column(cr, "purchase_order", "locked", "boolean")
    util.explode_execute(
        cr,
        """
            UPDATE purchase_order o
               SET locked = true
              FROM res_company c
             WHERE c.id = o.company_id
               AND c.po_lock = 'lock'
               AND o.state = 'done'
        """,
        alias="o",
        table="purchase_order",
    )
    util.change_field_selection_values(cr, "purchase.order", "state", {"done": "purchase"})
