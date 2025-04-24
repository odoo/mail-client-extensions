from odoo.upgrade import util


def migrate(cr, version):
    util.replace_record_references(
        cr,
        ("mail.activity.type", util.ref(cr, "product_expiry.mail_activity_type_alert_date_reached")),
        ("mail.activity.type", util.ref(cr, "mail.mail_activity_data_todo")),
        replace_xmlid=False,
    )
    util.delete_unused(cr, "product_expiry.mail_activity_type_alert_date_reached")
