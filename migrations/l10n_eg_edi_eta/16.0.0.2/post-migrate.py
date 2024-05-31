from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_ui_view
           SET type = 'form'
         WHERE id = %s
           AND type = 'tree'
        """,
        [util.ref(cr, "l10n_eg_edi_eta.product_normal_form_view_inherit_l10n_eg_eta_edi")],
    )
