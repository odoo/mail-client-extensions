from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    Journal = util.env(cr)["account.journal"]
    cr.execute(
        """
        SELECT j.id, a.alias_name
          FROM account_journal j
          JOIN mail_alias a ON j.alias_id = a.id
    """
    )
    for journal_id, alias_name in cr.fetchall():
        # We want to update the alias but leave the name intact
        Journal.browse(journal_id)._update_mail_alias({"alias_name": alias_name})

    util.if_unchanged(cr, "account.data_account_type_current_liabilities", util.update_record_from_xml)
