# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        DELETE FROM ir_model_data
              WHERE module = 'l10n_be_intrastat'
                AND model = 'l10n_be_intrastat.region'
    """
    )

    for x in {
        "cust_invoice",
        "supp_invoice",
        "invoice_line",
        "product_category",
        "res_company_form",
        "stock_warehouse_form",
    }:
        util.remove_view(cr, "l10n_be_intrastat.l10n_be_intrastat_xml_decl_{}_view".format(x))

    util.remove_model(cr, "l10n_be_intrastat_xml.xml_decl")
