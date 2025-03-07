from odoo.upgrade import util

script = util.import_script("product/saas~18.3.1.2/pre-migrate.py")


def migrate(cr, version):
    script.set_product_manager(cr, "sales_team.group_sale_manager")
