from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_plm.mrp_eco_bom_change_view_form")
    util.remove_view(cr, "mrp_plm.mrp_eco_routing_change_view_form")
    util.remove_field(cr, "mrp.eco.routing.change", "old_time_cycle_manual")
    util.remove_field(cr, "mrp.eco.routing.change", "new_time_cycle_manual")
    util.rename_xmlid(
        cr,
        "mrp_plm.product_template_only_form_inherit_version_plm",
        "mrp_plm.product_template_form_view",
    )
    util.if_unchanged(cr, "mrp_plm.product_template_form_view", util.update_record_from_xml)
    util.remove_view(cr, "mrp_plm.product_normal_form_view_inherit_version_plm")
    util.remove_view(cr, "mrp_plm.view_document_search_mrp_plm")
    util.rename_field(cr, "mrp.eco", "mrp_document_count", "document_count")
    util.rename_field(cr, "mrp.eco", "mrp_document_ids", "document_ids")
