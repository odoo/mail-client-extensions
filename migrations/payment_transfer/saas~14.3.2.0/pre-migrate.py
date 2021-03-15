from odoo.upgrade import util


def migrate(cr, version):

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_transfer.transfer_form")

    util.rename_xmlid(
        cr, "payment_transfer.payment_acquirer_view_form_inherit_transfer", "payment_transfer.payment_acquirer_form"
    )
