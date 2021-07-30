from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, xml_id="payment_ogone.redirect_form_validation")
    util.remove_view(cr, xml_id="payment_ogone.directlink_feedback")
