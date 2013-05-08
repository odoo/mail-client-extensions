# -*- coding: utf-8 -*-
import openerp

def migrate(cr, version):
    """if multiple sales teams were defined in 7.0, we must automatically
       check the option "Setting/Sales/Organize Sales activities into
       multiple Sales Team" otherwise Sales Teams are not visible on Leads and
       Opportunities
    """

    cr.execute('SELECT count(1) FROM crm_case_section WHERE active')
    count = cr.fetchone()[0]
    if count <= 1:
        return

    registry = openerp.modules.registry.RegistryManager.get(cr.dbname)
    settings = registry['sale.config.settings']

    sid = settings.create(cr, openerp.SUPERUSER_ID, {
        'group_multi_salesteams': True,
    })
    settings.execute(cr, openerp.SUPERUSER_ID, [sid])
