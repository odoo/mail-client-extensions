# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    """
    It is no longer legally required to keep daily sales book.
    """
    util.remove_view(cr, "l10n_cl_edi_boletas.dss_template")
    util.remove_view(cr, "l10n_cl_edi_boletas.daily_sales_book_subtemplate")
    util.remove_field(cr, "account.move", "l10n_cl_daily_sales_book_id")
    util.remove_model(cr, "l10n_cl.daily.sales.book")
