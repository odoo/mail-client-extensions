from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "mrp_workorder_plm.ecotype_workorder", "mrp_plm.ecotype_bom_update")
    util.rename_xmlid(cr, "mrp_workorder_plm.ecostage_new", "mrp_plm.ecostage_bom_update_new")
    util.rename_xmlid(cr, "mrp_workorder_plm.ecostage_progress", "mrp_plm.ecostage_bom_update_progress")
    util.rename_xmlid(cr, "mrp_workorder_plm.ecostage_validated", "mrp_plm.ecostage_bom_update_validated")
    util.rename_xmlid(cr, "mrp_workorder_plm.ecostage_effective", "mrp_plm.ecostage_bom_update_effective")
