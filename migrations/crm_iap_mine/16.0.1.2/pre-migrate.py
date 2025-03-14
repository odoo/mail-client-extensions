from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "crm_iap_mine.crm_lead_view_kanban_lead")
    util.remove_view(cr, "crm_iap_mine.crm_lead_view_kanban_opportunity")
