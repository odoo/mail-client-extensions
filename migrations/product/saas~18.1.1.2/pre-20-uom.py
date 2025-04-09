from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT 1 FROM uom_uom WHERE parent_path IS NULL LIMIT 1")
    if cr.rowcount:
        util.env(cr)["uom.uom"]._parent_store_compute()
