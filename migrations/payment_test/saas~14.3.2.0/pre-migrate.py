from odoo.upgrade import util


def migrate(cr, version):

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_test.test_s2s_form")
