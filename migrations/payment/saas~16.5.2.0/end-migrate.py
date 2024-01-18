from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    # Activate default pms for active providers.
    providers = env["payment.provider"].search([("state", "!=", "disabled")])
    providers._activate_default_pms()
