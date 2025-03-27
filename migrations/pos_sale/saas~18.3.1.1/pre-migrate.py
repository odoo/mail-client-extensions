from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_sale.res_partner_view_buttons_pos_sale")
    util.remove_view(cr, "pos_sale.crm_team_view_kanban_dashboard")
    util.remove_field(cr, "crm.team", "pos_sessions_open_count")
    util.remove_field(cr, "crm.team", "pos_order_amount_total")
