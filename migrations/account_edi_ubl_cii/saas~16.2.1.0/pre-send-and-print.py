# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(
        cr,
        *[
            f"account_edi_ubl_cii.{fmt}"
            for fmt in {
                "edi_facturx_1_0_05",
                "edi_nlcius_1",
                "ubl_bis3",
                "ubl_de",
                "edi_ubl_2_1",
                "edi_efff_1",
                "ubl_a_nz",
                "ubl_sg",
            }
        ],
    )
