from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order", "receipt_reminder_email", "BOOLEAN")
    util.create_column(cr, "purchase_order", "reminder_date_before_receipt", "INTEGER")

    util.explode_execute(
        cr,
        """
            UPDATE purchase_order po
                SET receipt_reminder_email = BOOL(partner.receipt_reminder_email->>TEXT(po.company_id)),
                    reminder_date_before_receipt = CAST(partner.reminder_date_before_receipt->>TEXT(po.company_id) AS INT)
                FROM res_partner partner
                WHERE po.partner_id = partner.id
        """,
        table="purchase_order",
        alias="po",
    )

    util.remove_field(cr, "purchase.order", "mail_reminder_confirmed")
    util.remove_field(cr, "purchase.order", "mail_reception_confirmed")
    util.remove_field(cr, "purchase.order", "mail_reception_declined")
    util.remove_field(cr, "res.config.settings", "default_purchase_method")
