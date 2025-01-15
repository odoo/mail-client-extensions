from odoo.upgrade.util import remove_record


def migrate(cr, version):
    remove_record(cr, "website_mail_group.s_group_000_js")
