from odoo.upgrade import util


def migrate(cr, version):
    if util.has_design_themes():
        cr.execute(
            """
            UPDATE ir_asset
               SET path = '/website/static/src/interactions/ripple_effect.js'
             WHERE path = '/website/static/src/js/content/ripple_effect.js'
            """
        )
