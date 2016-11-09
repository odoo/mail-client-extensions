# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_data
           SET noupdate=false
         WHERE module='l10n_nl'
           AND model like '%.template'
    """)

    util.rename_xmlid(
        cr,
        *util.expand_braces('l10n_nl.fiscal_position_template_{domestic,national}')
    )
