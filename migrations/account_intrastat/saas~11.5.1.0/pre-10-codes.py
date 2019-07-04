# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # Change old model -> new one
    # Doing this avoid to alter account.invoice.line
    util.rename_model(cr, "report.intrastat.code", "account.intrastat.code")
    if util.module_installed(cr, "l10n_be_intrastat"):
        cr.execute("alter table l10n_be_intrastat_transaction DROP CONSTRAINT l10n_be_intrastat_transaction_l10n_be_intrastat_trcodeunique")

    # This way, we avoid to move value from name to code for thousands of records
    util.rename_field(cr, "account.intrastat.code", "name", "code")
    util.create_column(cr, "account_intrastat_code", "name", "varchar")
    util.create_column(cr, "account_intrastat_code", "type", "varchar")
    cr.execute("update account_intrastat_code set type='commodity'")

    # change xmlids
    if util.module_installed(cr, "l10n_be_intrastat"):
        cr.execute(
            r"""
            UPDATE ir_model_data
               SET module='account_intrastat',
                     name='commodity_code_2018_' || substring(name, 25)
             WHERE module='l10n_be_intrastat'
               AND name LIKE 'intrastat\_category\_2014\_%'
        """
        )

        util.move_field_to_module(cr, "account.invoice", "intrastat_country_id", "l10n_be_intrastat", "account_intrastat")
        util.move_field_to_module(cr, "product.category", "intrastat_id", "l10n_be_intrastat", "account_intrastat")
        util.move_field_to_module(cr, "res.company", "incoterm_id", "l10n_be_intrastat", "account_intrastat")
