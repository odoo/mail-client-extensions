# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "crm_reveal_rule", "filter_on_size", 'boolean')
    util.create_column(cr, "crm_reveal_rule", "contact_filter_type", "varchar")
    util.remove_field(cr, "crm.reveal.rule", "calculate_credits")

    cr.execute("""
        UPDATE crm_reveal_rule
           SET filter_on_size = company_size_max > 0,
               contact_filter_type = 'role'
    """)
    cr.execute("UPDATE crm_reveal_rule SET extra_contacts = 1 WHERE extra_contacts = 0")
