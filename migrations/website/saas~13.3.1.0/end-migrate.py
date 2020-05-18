# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        r"""
        UPDATE ir_ui_view
           SET active=true
         WHERE key ~ '\.[_]{0,1}assets_snippet_s_.*_000'
    """
    )
