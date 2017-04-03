# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'mrp.production', 'check_todo', 'quality_check_todo')
    util.rename_field(cr, 'mrp.production', 'alert_ids', 'quality_alert_ids')
    util.rename_field(cr, 'mrp.production', 'alert_count', 'quality_alert_count')

    util.rename_field(cr, 'mrp.workorder', 'check_todo', 'quality_check_todo')
    util.rename_field(cr, 'mrp.workorder', 'alert_count', 'quality_alert_count')

    util.rename_field(cr, 'quality.alert', 'operation_id', 'workorder_id')
