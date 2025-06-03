from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    for website in env["website"].search([]):
        website._create_checkout_steps()
