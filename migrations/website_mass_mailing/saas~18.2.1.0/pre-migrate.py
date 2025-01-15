from odoo.upgrade.util import remove_record


def migrate(cr, version):
    remove_record(cr, "website_mass_mailing.s_popup_000_js")
