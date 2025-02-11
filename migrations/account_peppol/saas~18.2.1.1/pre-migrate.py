from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "account_peppol.service.wizard")
    util.remove_column(cr, "peppol_registration", "smp_registration")  # not stored anymore
