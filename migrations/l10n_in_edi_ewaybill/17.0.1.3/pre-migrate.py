def migrate(cr, version):
    cr.execute(
        """
        DELETE FROM account_edi_format_account_journal_rel aef_aj_rel
              USING account_edi_format aef
              WHERE aef.code = 'in_ewaybill_1_03'
                AND aef_aj_rel.account_edi_format_id = aef.id
        """
    )
