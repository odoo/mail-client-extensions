from odoo.upgrade import util


def migrate(cr, version):
    post_migrate = util.import_script("account/saas~17.4.1.2/pre-migrate.py")
    post_migrate.update_pos_receipt_labels(cr, "=", "it")
