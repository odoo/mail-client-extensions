from odoo.upgrade import util

script = util.import_script("payment/saas~16.5.2.0/end-migrate.py")


def migrate(cr, version):
    xmlid = "payment_ogone.payment_provider_ogone"
    util.update_record_from_xml(cr, xmlid)
    script.copy_payment_methods_to_duplicated_providers(cr, xmlid)
    script.activate_default_pms(cr, code="ogone")
