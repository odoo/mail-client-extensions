# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'res.partner', 'commercial_partner_country_id')
    util.remove_field(cr, 'res.users', 'commercial_partner_country_id', drop_column=False)
    util.remove_field(cr, 'res.groups', 'is_portal')

    util.move_model(cr, 'base.partner.merge.line', 'crm', 'base')
    util.move_model(cr, 'base.partner.merge.automatic.wizard', 'crm', 'base')

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('{crm,base}.action_partner_deduplicate'))
    util.rename_xmlid(cr, *eb('{crm,base}.base_partner_merge_automatic_wizard_form'))
    util.rename_xmlid(cr, *eb('{crm,base}.action_partner_merge'))
