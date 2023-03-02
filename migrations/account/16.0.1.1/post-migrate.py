from odoo import modules


def migrate(cr, version):
    l10n_modules = [m for m in modules.get_modules() if m.startswith("l10n_")]
    cr.execute(
        r"""
            UPDATE ir_attachment att
               SET public = True
              FROM ir_model_data imd
             WHERE att.name ~* '\.xsd$'
               AND att.public IS NULL
               AND att.id = imd.res_id
               AND imd.module IN %s
               AND imd.model = 'ir.attachment'
            """,
        [tuple(l10n_modules)],
    )
