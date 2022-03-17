# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_ticket", "partner_phone", "varchar")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
                UPDATE helpdesk_ticket ticket
                   SET partner_phone = partner.phone
                  FROM res_partner partner
                 WHERE partner.id = ticket.partner_id
            """,
            table="helpdesk_ticket",
            alias="ticket",
        ),
    )
