# -*- coding: utf-8 -*-
def migrate(cr, version):
    # in 8.0, size has been removed from a lot of varchar fields
    # to be successful, we need to drop views that depends on these fields
    # NOTE not all views are listed here, only the ones that forbid migration
    # NOTE some views are relics from 6.1
    views = [
        'report_files_partner',
    ]

    for v in views:
        cr.execute('DROP VIEW IF EXISTS "%s"' % (v,))
