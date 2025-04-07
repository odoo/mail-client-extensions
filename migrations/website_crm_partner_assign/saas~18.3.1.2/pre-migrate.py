from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_crm_partner_assign.crm_menu_resellers")
    util.remove_record(cr, "website_crm_partner_assign.menu_res_partner_grade_action")
    util.remove_view(cr, "website_crm_partner_assign.res_partner_grade_view_search")
    util.remove_view(cr, "website_crm_partner_assign.view_partner_grade_tree")
    util.remove_view(cr, "website_crm_partner_assign.view_res_partner_filter_assign")
