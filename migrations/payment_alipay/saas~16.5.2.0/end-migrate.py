from odoo.upgrade import util

script = util.import_script("payment/saas~16.5.2.0/end-migrate.py")


def migrate(cr, version):
    xmlid = "payment_alipay.payment_provider_alipay"
    util.update_record_from_xml(cr, xmlid)
    script.copy_payment_methods_to_duplicated_providers(cr, xmlid)
