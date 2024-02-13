from odoo.upgrade import util

script = util.import_script("payment/saas~16.5.2.0/end-migrate.py")


def migrate(cr, version):
    xmlid = "website_sale_ups.payment_provider_ups_cod"
    util.update_record_from_xml(cr, xmlid)
    script.copy_payment_methods_to_duplicated_providers(cr, xmlid, custom_mode="cash_on_delivery")
