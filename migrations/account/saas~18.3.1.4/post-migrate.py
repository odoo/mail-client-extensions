from odoo.upgrade import util

script = util.import_script("product/saas~18.3.1.2/pre-migrate.py")


def migrate(cr, version):
    util.if_unchanged(cr, "account.account_invoice_rule_portal", util.update_record_from_xml)
    util.if_unchanged(cr, "account.account_invoice_line_rule_portal", util.update_record_from_xml)
    util.update_record_from_xml(cr, "account.europe_vat", force_create=False, fields=["code"])

    script.set_product_manager(cr, "account.group_account_manager")
