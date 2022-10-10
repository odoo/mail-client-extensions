# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE res_partner
        SET company_registry = l10n_rs_company_registry
        WHERE l10n_rs_company_registry IS NOT NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="res_partner"))
    util.remove_constraint(cr, "res_partner", "company_registry_country_uniq")
    util.remove_field(cr, "account.move", "l10n_rs_company_registry")
    util.remove_field(cr, "res.partner", "l10n_rs_company_registry")
    util.remove_view(cr, "l10n_rs.view_partner_form_inherit")
