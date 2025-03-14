from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM account_journal journal
          JOIN res_company company ON company.id=journal.company_id
         WHERE journal.l10n_in_gstin_partner_id IS NOT NULL
           AND journal.l10n_in_gstin_partner_id != company.partner_id
        """
    )
    if cr.rowcount:
        message = """
        You are using Multi-GSTIN which is deprecated now
        because per GSTIN you need to create a company.
        there are many complications to using Multi-GSTIN.
        As per GST integrations like E-invoice, E-waybill, and GST E-filing we need separate companies.

        So we suggest to create a company for each GSTIN.
        """
        util.add_to_migration_reports(message, "Accounting")
    util.remove_field(cr, "account.journal", "l10n_in_gstin_partner_id")
    util.remove_view(cr, "l10n_in.l10n_in_external_layout")
