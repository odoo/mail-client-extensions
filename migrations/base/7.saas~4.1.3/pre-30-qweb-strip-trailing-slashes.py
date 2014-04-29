# -*- coding: utf-8 -*-

def migrate(cr, version):
    """In saas-4 all routes have been stripped from their trailing slashes.
        remove them from `noupdate`able qweb views
    """

    # as "Lookahead constraints cannot contain back references" we need to match both,
    # single and double quotes

    rxp = r'((?:action|href)="(?!https?)[^"]+?)/(\?[^"]*?)*(")'
    for r in [rxp, rxp.replace('"', "'")]:
        cr.execute("""UPDATE ir_ui_view v
                         SET arch = regexp_replace(arch, %s, %s, 'mg')
                       WHERE type='qweb'
                         AND EXISTS(SELECT 1
                                      FROM ir_model_data
                                     WHERE model='ir.ui.view'
                                       AND res_id=v.id
                                       AND noupdate='t')
                          OR NOT EXISTS(SELECT 1
                                          FROM ir_model_data
                                         WHERE model='ir.ui.view'
                                           AND res_id=v.id)
                    """, (r, r'\1\2\3'))
