# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "helpdesk_sla_helpdesk_stage_rel", "helpdesk_sla", "helpdesk_stage")

    cr.execute(
        """
        INSERT INTO helpdesk_sla_helpdesk_stage_rel
               (helpdesk_sla_id, helpdesk_stage_id)
        SELECT s.id, s.exclude_stage_id
        FROM helpdesk_sla s
        WHERE s.exclude_stage_id IS NOT NULL"""
    )

    util.remove_field(cr, "helpdesk.sla", "exclude_stage_id")
