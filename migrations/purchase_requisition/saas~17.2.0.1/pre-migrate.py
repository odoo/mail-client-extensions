from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "purchase.requisition", "origin", "reference")
    util.rename_field(cr, "purchase.requisition", "ordering_date", "date_start")
    util.create_column(
        cr,
        "purchase_requisition",
        "requisition_type",
        "varchar",
        default="blanket_order",
    )

    util.change_field_selection_values(
        cr,
        "purchase.requisition",
        "state",
        {"in_progress": "confirmed", "open": "confirmed", "ongoing": "confirmed"},
    )

    util.explode_execute(
        cr,
        """
            UPDATE purchase_requisition pr
               SET requisition_type = 'purchase_template'
              FROM purchase_requisition_type prt
             WHERE prt.id = pr.type_id
               AND prt.quantity_copy = 'copy'
        """,
        table="purchase_requisition",
        alias="pr",
    )

    util.alter_column_type(cr, "purchase_requisition", "date_end", "date")
    util.remove_field(cr, "purchase.requisition", "state_blanket_order")
    util.remove_field(cr, "purchase.requisition", "type_id")
    util.remove_model(cr, "purchase.requisition.type")
    util.remove_field(cr, "purchase.requisition", "is_quantity_copy")
    util.remove_field(cr, "purchase.order", "is_quantity_copy")
    util.remove_field(cr, "purchase.requisition", "schedule_date")
    util.remove_field(cr, "purchase.requisition.line", "schedule_date")
