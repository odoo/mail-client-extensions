from odoo.upgrade import util

post_migrate = util.import_script("payment/saas~16.5.2.0/post-migrate.py")


def migrate(cr, version):
    util.update_record_from_xml(cr, "payment_demo.payment_method_demo", from_module="payment_demo")
    xmlid_provider = "payment.payment_provider_demo"
    util.update_record_from_xml(cr, xmlid_provider, from_module="payment_demo")
    post_migrate.copy_payment_methods_to_duplicated_providers(cr, xmlid_provider)
