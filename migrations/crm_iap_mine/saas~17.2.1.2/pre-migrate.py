from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.iap.lead.mining.request", "display_lead_label")
