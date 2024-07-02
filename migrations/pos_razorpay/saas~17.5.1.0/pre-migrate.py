from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE pos_payment pp
           SET cardholder_name = pp.razorpay_card_owner_name,
                card_brand = pp.razorpay_card_scheme,
                card_no = pp.razorpay_issuer_card_no,
                payment_ref_no = pp.razorpay_reference_no,
                payment_method_authcode = pp.razorpay_authcode,
                payment_method_issuer_bank = pp.razorpay_issuer_bank,
                payment_method_payment_mode = pp.razorpay_payment_method
          FROM pos_payment_method pm
         WHERE pm.id = pp.payment_method_id
           AND pm.use_payment_terminal = 'razorpay';
        """
    )
    util.remove_view(cr, "pos_razorpay.view_pos_payment_form")
    util.remove_field(cr, "pos.payment", "razorpay_card_owner_name")
    util.remove_field(cr, "pos.payment", "razorpay_card_scheme")
    util.remove_field(cr, "pos.payment", "razorpay_reference_no")
    util.remove_field(cr, "pos.payment", "razorpay_payment_method")
    util.remove_field(cr, "pos.payment", "razorpay_issuer_bank")
    util.remove_field(cr, "pos.payment", "razorpay_issuer_card_no")
    util.remove_field(cr, "pos.payment", "razorpay_authcode")
