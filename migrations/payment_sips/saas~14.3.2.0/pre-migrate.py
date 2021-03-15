from odoo.upgrade import util


def migrate(cr, version):

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_sips.sips_form")

    util.rename_xmlid(cr, "payment_sips.acquirer_form_sips", "payment_sips.payment_acquirer_form")
