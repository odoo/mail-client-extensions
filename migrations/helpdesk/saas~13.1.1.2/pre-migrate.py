# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Cannot show ratings in portal if not using them
    cr.execute("UPDATE helpdesk_team SET portal_show_rating = false WHERE use_rating = false")

    util.remove_field(cr, "helpdesk.team", "use_api")

    util.create_column(cr, "helpdesk_sla", "target_type", "varchar")
    util.create_column(cr, "helpdesk_sla", "time_minutes", "integer")
    util.create_column(cr, "helpdesk_sla_status", "target_type", "varchar")

    cr.execute("UPDATE helpdesk_sla SET target_type = 'stage', time_minutes = 0")
    # stored related to sla, but all sla have the same value
    cr.execute("UPDATE helpdesk_sla_status SET target_type = 'stage'")

    # views
    util.remove_view(cr, "helpdesk.index")
