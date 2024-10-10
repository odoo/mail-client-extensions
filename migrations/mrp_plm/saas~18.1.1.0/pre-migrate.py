from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "mrp_eco_approval", "name")
    util.remove_column(cr, "mrp_eco_approval", "template_stage_id")
    util.remove_column(cr, "mrp_eco_approval", "eco_stage_id")
    util.remove_column(cr, "mrp_eco", "new_bom_revision")
