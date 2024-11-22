from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "crm_lead", "email_domain_criterion", "varchar")
