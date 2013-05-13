# -*- coding: utf-8 -*-
def migrate(cr, version):
    """In 7.0, the module "account_report_company" was a temporary module and
       it functionnality is now part of the "account" module."""

    cr.execute("""
        UPDATE ir_module_module
           SET state= CASE WHEN state = %(toinstall)s THEN %(uninstalled)s ELSE %(toremove)s END
         WHERE name=%(name)s
           AND state in %(states)s
    """, {
        'toremove': 'to remove',
        'toinstall': 'to install',
        'uninstalled': 'uninstalled',
        'name': 'account_report_company',
        'states': ('installed', 'to install', 'to upgrade'),
    })
