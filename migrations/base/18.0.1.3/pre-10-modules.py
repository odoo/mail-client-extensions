from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_es_edi_tbai_multi_refund", "l10n_es_edi_tbai")
