# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute("SELECT code,id FROM account_edi_format WHERE code in ('ehf_3', 'ubl_bis3')")
    code_ids = dict(cr.fetchall())
    if "ehf_3" not in code_ids:
        return

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
        cr, ("account.edi.format", code_ids["ehf_3"]), ("account.edi.format", code_ids["ubl_bis3"]), replace_xmlid=False
    )
    util.remove_record(cr, ("account.edi.format", code_ids["ehf_3"]))
