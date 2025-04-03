from odoo.upgrade import util


def migrate(cr, version):
    model = "pos.prep.order" if util.version_gte("saas~18.3") else "pos_preparation_display.order"
    util.remove_field(cr, model, "pos_takeaway")
