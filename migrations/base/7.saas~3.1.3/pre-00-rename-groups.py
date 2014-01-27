# -*- coding: utf-8 -*-
def migrate(cr, version):

    groups = {
        'portal.group_anonymous': 'group_public',
        'portal.group_portal': 'group_portal',
    }

    for old, new in groups.items():
        module, _, xname = old.partition('.')

        cr.execute("""UPDATE ir_model_data
                         SET noupdate=%s
                             module=%s
                             name=%s
                       WHERE module=%s
                         AND name=%s
                   """, (False, 'base', new, module, xname))
