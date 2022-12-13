# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Records with XML ids mod_347_operations_real_estates_bought and mod_347_operations_regular_sold
    # were swapped in 12.0
    if util.version_between("saas~12.3", "14.0"):
        for xmlid, codes in [
            ("mod_347_operations_regular_bought", ("_mod_347_temp", "aeat_mod_347_operations_regular_bought")),
            ("mod_347_operations_regular_sold", ("aeat_mod_347_operations_regular_sold",)),
        ]:
            cr.execute(
                """
                    UPDATE ir_model_data
                       SET noupdate = false,
                           res_id = (
                            SELECT id
                              FROM account_financial_html_report_line
                             WHERE code in %s
                            )
                     WHERE module = 'l10n_es_reports' AND name = %s
                """,
                (codes, xmlid),
            )
