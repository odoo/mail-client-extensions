# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("UPDATE utm_campaign SET stage_id=%s WHERE stage_id IS NULL", [util.ref(cr, "utm.default_utm_stage")])
    cr.execute("ALTER TABLE utm_campaign ALTER COLUMN stage_id SET NOT NULL")
