from odoo.upgrade import util

post_migrate = util.import_script("payment/saas~16.5.2.0/post-migrate.py")


def migrate(cr, version):
    xmlid = "payment_alipay.payment_provider_alipay"
    util.update_record_from_xml(cr, xmlid)
    post_migrate.copy_payment_methods_to_duplicated_providers(cr, xmlid)
