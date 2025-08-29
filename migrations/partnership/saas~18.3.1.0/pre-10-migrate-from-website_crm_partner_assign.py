from odoo.upgrade import util


def migrate(cr, version):
    for record in [
        "view_partner_grade_tree",
        "res_partner_grade_view_search",
        "view_res_partner_filter_assign",
        "res_partner_grade_action",
    ]:
        util.rename_xmlid(cr, f"website_crm_partner_assign.{record}", f"partnership.{record}")

    util.move_field_to_module(cr, "res.partner", "grade_id", "website_crm_partner_assign", "partnership")
    util.move_model(
        cr,
        "res.partner.grade",
        "website_crm_partner_assign",
        "partnership",
        move_data=True,
    )
    # move back the only field that remains in website_crm_partner_assign
    util.move_field_to_module(cr, "res.partner.grade", "partner_weight", "partnership", "website_crm_partner_assign")
    # move back fields from website.published.mixin
    util.move_field_to_module(cr, "res.partner.grade", "website_published", "partnership", "website_crm_partner_assign")
    util.move_field_to_module(cr, "res.partner.grade", "is_published", "partnership", "website_crm_partner_assign")
    util.move_field_to_module(cr, "res.partner.grade", "can_publish", "partnership", "website_crm_partner_assign")
    util.move_field_to_module(cr, "res.partner.grade", "website_url", "partnership", "website_crm_partner_assign")
    util.move_field_to_module(
        cr, "res.partner.grade", "website_absolute_url", "partnership", "website_crm_partner_assign"
    )
