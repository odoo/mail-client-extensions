from odoo.upgrade import util


def migrate(cr, version):
    mapping = {
        util.ref(cr, "documents_account.mail_documents_activity_data_vat"): util.ref(
            cr, "mail.mail_activity_data_todo"
        ),
        util.ref(cr, "documents_account.mail_documents_activity_data_fs"): util.ref(cr, "mail.mail_activity_data_todo"),
    }
    util.replace_record_references_batch(
        cr,
        mapping,
        "mail.activity.type",
        replace_xmlid=False,
    )
    util.delete_unused(
        cr, "documents_account.mail_documents_activity_data_vat", "documents_account.mail_documents_activity_data_fs"
    )
