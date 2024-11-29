from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "account.move.send.wizard", "mail_template_id", "template_id")
    util.rename_field(cr, "account.move.send.wizard", "mail_lang", "lang")
    util.rename_field(cr, "account.move.send.wizard", "mail_subject", "subject")
    util.rename_field(cr, "account.move.send.wizard", "mail_body", "body")

    util.remove_field(cr, "account.move.send.wizard", "is_download_only")
