from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "auth_oauth.provider_openerp", fields=["css_class", "body"])
    util.update_record_from_xml(cr, "auth_oauth.provider_facebook", fields=["css_class", "body"])
    util.update_record_from_xml(cr, "auth_oauth.provider_google", fields=["css_class", "body"])
