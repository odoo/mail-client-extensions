from odoo.upgrade import util


def migrate(cr, version):
    # Remove demo pricelist_data entries from the database as it was moved to 'demo' in v18.1
    cr.execute("SELECT 1 FROM ir_module_module WHERE name='pos_pricer' AND demo IS True")
    if not cr.rowcount and not util.delete_unused(cr, "pos_pricer.pricer_demo_pricelist"):
        util.force_noupdate(cr, "pos_pricer.pricer_demo_pricelist_item", noupdate=True)
