# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    candidates = {
        'account_accountant': 'account_accountant_tour',
        'crm': 'crm_tour',
        'hr_expense': 'hr_expense_tour',
        'hr_recruitment': 'hr_recruitment_tour',
        'mail': 'mail_tour',
        'point_of_sale': 'point_of_sale_tour',
        'project': 'project_tour',
        'sale': 'sale_tour',

        'website': 'banner',
        'website_blog': 'blog',
        'website_event': 'event',
        'website_forum': 'question',
        'website_sale': 'shop',
    }
    tours = [tour for module, tour in candidates.items() if util.module_installed(cr, module)]
    if not tours:
        return      # at least `mail` should be installed

    gid = util.ref(cr, 'base.group_user')
    cr.execute("""
        INSERT INTO web_tour_tour(user_id, name)
             SELECT uid, name
               FROM res_groups_users_rel,
                    (SELECT unnest(%s) AS name) AS tours
              WHERE gid = %s
    """, [tours, gid])
