from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sign.mail_activity_type_form_inherit")
    util.remove_view(cr, "sign.encrypted_ask_password")

    # Remove related field
    util.remove_field(cr, "sign.template", "datas")

    # Remove deprecated fields without dropping (handled in post-migrate)
    util.remove_field(cr, "sign.template", "num_pages", drop_column=False)
    util.remove_field(cr, "sign.template", "attachment_id", drop_column=False)
    util.remove_field(cr, "sign.request", "completed_document", keep_as_attachments=True)
