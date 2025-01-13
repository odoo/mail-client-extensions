from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_din5008_purchase.report_common_purchase_din5008_template")
