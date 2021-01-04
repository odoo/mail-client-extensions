# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
        UPDATE ir_ui_view
           SET active=true
         WHERE key ~ '\.[_]{0,1}assets_snippet_s_.*_000'
    """
    )

    # helper asset view has been split (see odoo/odoo@da46ba7bc1af7e192ffaed654eee82d0a8ef90be)
    # change parent of potential custom views (created by web_editor (save_asset method))
    cr.execute(
        r"""
        UPDATE ir_ui_view
           SET inherit_id = %s
         WHERE inherit_id = %s
           AND arch_db LIKE '%%/website/static/src/scss/user\_custom\_bootstrap\_overridden.scss%%'
        """,
        [
            util.ref(cr, "website._assets_frontend_helpers_user_custom"),
            util.ref(cr, "website._assets_frontend_helpers"),
        ],
    )

    cr.execute(
        r"""
        UPDATE ir_ui_view
           SET inherit_id = %s
         WHERE inherit_id = %s
           AND arch_db LIKE '%%/website/static/src/scss/user\_custom\_rules.scss%%'
        """,
        [
            util.ref(cr, "website.assets_frontend_user_custom"),
            util.ref(cr, "website.assets_frontend"),
        ],
    )
