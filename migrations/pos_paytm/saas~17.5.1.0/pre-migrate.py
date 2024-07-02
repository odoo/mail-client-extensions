from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE pos_payment pp
           SET card_brand = pp.paytm_card_scheme,
                card_no = pp.paytm_issuer_card_no,
                payment_ref_no = pp.paytm_reference_no,
                payment_method_authcode = pp.paytm_authcode,
                payment_method_issuer_bank = pp.paytm_issuer_bank,
                payment_method_payment_mode = pp.paytm_payment_method
          FROM pos_payment_method pm
         WHERE pm.id = pp.payment_method_id
           AND pm.use_payment_terminal = 'paytm';
        """
    )
    util.remove_view(cr, "pos_paytm.view_pos_payment_form")
    util.remove_field(cr, "pos.payment", "paytm_card_scheme")
    util.remove_field(cr, "pos.payment", "paytm_reference_no")
    util.remove_field(cr, "pos.payment", "paytm_payment_method")
    util.remove_field(cr, "pos.payment", "paytm_issuer_bank")
    util.remove_field(cr, "pos.payment", "paytm_issuer_card_no")
    util.remove_field(cr, "pos.payment", "paytm_authcode")
