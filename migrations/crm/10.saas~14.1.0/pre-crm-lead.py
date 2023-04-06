# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, 'crm.lead', 'date_action', 'activity_date_deadline')

    fields_refs = {
        'next_activity_id': 'activity_ids',
        'date_action_next': 'activity_date_deadline',
        'date_action_last': 'write_date',       # no better alternative...
        'title_action': 'activity_summary',
    }
    for old, new in fields_refs.items():
        util.update_field_usage(cr, "crm.lead", old, new)
