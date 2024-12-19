from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_uk_hmrc.hmrc_transaction_engine_request")
    util.remove_view(cr, "l10n_uk_hmrc.hmrc_transaction_engine_base")
