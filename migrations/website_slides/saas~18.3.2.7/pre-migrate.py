from odoo.upgrade import util


def migrate(cr, version):
    util.replace_record_references(
        cr,
        ("mail.activity.type", util.ref(cr, "website_slides.mail_activity_data_access_request")),
        ("mail.activity.type", util.ref(cr, "mail.mail_activity_data_todo")),
        replace_xmlid=False,
    )
    util.delete_unused(cr, "website_slides.mail_activity_data_access_request")
