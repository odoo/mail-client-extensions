from odoo.upgrade import util


def migrate(cr, version):
    if util.create_column(cr, "res_partner", "vies_valid", "boolean"):
        # in case base_vat was force installed after 16.3
        util.import_script("base_vat/saas~16.3.1.0/pre-migrate.py").migrate(cr, version)
