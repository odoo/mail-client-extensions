# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    gone = """
        # account.fiscal.position.tax.template
        fp_tax_template_impexp_ha_encaissement
        fp_tax_template_impexp_ha_intermediaire
        fp_tax_template_impexp_ha_encaissement_super_reduite
        fp_tax_template_impexp_ha_encaissement_reduite

        # account.tax.template
        tva_import_0
    """
    for name in util.splitlines(gone):
        util.remove_record(cr, f"l10n_fr.{name}")
