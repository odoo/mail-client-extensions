# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    fmts_code = (
        "facturx_1_0_05",
        "nlcius_1",
        "ubl_bis3",
        "ubl_de",
        "ubl_2_1",
        "efff_1",
        "ubl_a_nz",
        "ubl_sg",
    )

    # Link the ubl_cii attachments: set the res_field for every ir_attachment linked to an account_edi_document
    query = cr.mogrify(
        """
        UPDATE ir_attachment a
           SET res_field = 'ubl_cii_xml_file'
          FROM account_edi_document doc
          JOIN account_edi_format fmt
            ON fmt.id = doc.edi_format_id
         WHERE doc.attachment_id = a.id
           AND a.res_model = 'account.move'
           AND a.res_id IS NOT NULL
           AND fmt.code IN %s
        """,
        [fmts_code],
    ).decode()
    util.explode_execute(cr, query, table="ir_attachment", alias="a")

    # Remove the account_edi_documents (the ORM will remove the account_edi_formats)
    cr.execute(
        """
        DELETE FROM account_edi_document doc
              USING account_edi_format fmt
              WHERE doc.edi_format_id = fmt.id AND fmt.code IN %s
        """,
        [fmts_code],
    )
