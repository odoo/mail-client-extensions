# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)
    util.move_field_to_module(cr, 'event.event', 'twitter_hashtag', 'website_event', 'event')
    util.create_column(cr, 'event_type', 'has_seats_limitation', 'boolean')
    util.create_column(cr, 'event_type', 'use_reply_to', 'boolean')
    util.create_column(cr, 'event_type', 'default_timezone', 'varchar')     # keep NULL
    # Let's ORM create and compute default value for other new fields
    cr.execute("""
        UPDATE event_type
           SET has_seats_limitation = (default_registration_min != 0
                                    OR default_registration_max != 0),
               use_reply_to = (coalesce(default_reply_to, '') != '')
    """)

    # auto_confirm: before => computed value from global ir.values; now => stored value from event.type setting
    util.create_column(cr, 'event_event', 'auto_confirm', 'boolean')
    auto_confirm = bool(env['ir.values'].get_default('event.config.settings', 'auto_confirmation')) or False
    cr.execute("UPDATE event_event SET auto_confirm = %s", (auto_confirm,))

    setting_fields = util.splitlines("""
        module_event_sale
        module_website_event_track
        module_website_event_questions
        module_event_barcode
        auto_confirmation
    """)
    for f in setting_fields:
        util.remove_field(cr, 'event.config.settings', f)

    util.delete_model(cr, 'report.event.registration')

    util.remove_view(cr, 'event.view_event_configuration')
