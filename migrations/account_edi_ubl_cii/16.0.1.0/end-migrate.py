from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute("SELECT code,id FROM account_edi_format WHERE code in ('ehf_3', 'ubl_bis3')")
    code_ids = dict(cr.fetchall())
    if "ehf_3" in code_ids:
        # Cleaning: removing the EHF3 edi.format since it is now full covered by the bis3 one
        # First, in the edi_document table, replace the links to EHF3 by BIS3.
        # Then, we can drop the EHF3 edi_format.

        # Warning ! If we have an edi_document with format BIS3 AND a document with format EHF3 for the same account_move,
        # a duplicate key error will be thrown when we replace the EHF3 format by the BIS3 one !
        # In this case, only keep the BIS3 edi_document, unlink the ehf3 one.
        if "ubl_bis3" in code_ids:
            cr.execute(
                """
                  SELECT doc1.id
                    FROM account_edi_document doc1
                    JOIN account_edi_document doc2
                      ON doc1.move_id = doc2.move_id
                   WHERE doc1.edi_format_id = %(ehf_3)s
                     AND doc2.edi_format_id = %(ubl_bis3)s
                """,
                code_ids,
            )
            util.iter_browse(env["account.edi.document"], [r[0] for r in cr.fetchall()]).unlink()

        # Now, we can replace the edi_documents with ehf_3 by bis3 and finally remove the ehf_3 edi_format
        util.replace_record_references(
            cr,
            ("account.edi.format", code_ids["ehf_3"]),
            ("account.edi.format", code_ids["ubl_bis3"]),
            replace_xmlid=False,
        )
        util.remove_record(cr, ("account.edi.format", code_ids["ehf_3"]))

    # Factur-X is now always generated silently, uncheck the Factur-X edi format for everyone except for those who enabled
    # the PDF/A3 system parameter (on their FR/DE journals). Keeping the Factur-X edi format option will validate the invoice and
    # show warnings and create a PDF/A-3 such that it works with Chorus Pro.
    cr.execute("SELECT value FROM ir_config_parameter WHERE key = 'edi.use_pdfa'")
    if cr.rowcount and util.str2bool(cr.fetchone()[0], default=False):
        # Uncheck Factur-X for all except on FR/DE journals
        cr.execute(
            """
            WITH to_delete AS (
                SELECT journal.id AS journal_id, format.id AS format_id
                  FROM account_journal journal
                  JOIN res_company ON res_company.id = journal.company_id
                  JOIN res_partner ON res_partner.id = res_company.partner_id
                  JOIN res_country ON res_partner.country_id = res_country.id
                  JOIN account_edi_format_account_journal_rel m2m ON m2m.account_journal_id = journal.id
                  JOIN account_edi_format format ON format.id = m2m.account_edi_format_id
                 WHERE res_country.code NOT IN ('FR', 'DE')
                   AND format.code = 'facturx_1_0_05'
            )
            DELETE FROM account_edi_format_account_journal_rel
                  WHERE (account_journal_id, account_edi_format_id)
                     IN (SELECT journal_id, format_id FROM to_delete)
            """
        )
    else:
        # Uncheck Factur-X for all
        cr.execute(
            """
            DELETE FROM account_edi_format_account_journal_rel
                  WHERE account_edi_format_id = (SELECT id
                                                   FROM account_edi_format
                                                  WHERE code = 'facturx_1_0_05')
        """
        )

    util.remove_record(cr, "account_edi_ubl_cii.ir_config_parameter_use_pdfa")
