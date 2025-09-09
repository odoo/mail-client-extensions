from odoo.upgrade import util


def migrate(cr, version):
    query = "SELECT id FROM crm_lead WHERE email_normalized IS NOT NULL"
    util.recompute_fields(cr, "crm.lead", ["email_domain_criterion"], query=query, chunk_size=1024)
