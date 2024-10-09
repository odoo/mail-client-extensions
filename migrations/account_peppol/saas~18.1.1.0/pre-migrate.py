from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "peppol.registration", "edi_mode_constraint")
    util.remove_record(cr, "account_peppol.default_account_peppol_mode_constraint")
