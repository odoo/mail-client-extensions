# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    # move down: quality -> quality_control
    cr.execute("""
        UPDATE ir_model_data
           SET module='quality_control'
         WHERE module='quality'
           AND model IN ('ir.ui.view',
                         'ir.actions.act_window',
                         'ir.ui.menu',
                         'quality.point.test_type',
                         'quality.point'
                        )
           AND name NOT IN ('quality_point_view_form')
    """)

    # move up: quality_mrp -> quality_control
    # (done here as we quality_mrp depends on quality_control)
    # quality_mrp and quality_mrp_workorder being sibling module, they may be loaded in
    # any order. Move stuff from here, before loading...

    util.rename_xmlid(cr, *eb('quality_{mrp,control}.quality_check_failure_message'))

    moved = util.splitlines("""
        mrp_workorder_view_form_inherit_{quality,workorder}
        mrp_workorder_view_form_tablet
        mrp_workorder_view_form_tablet_menu
        mrp_workorder_action_tablet
        quality_check_view_form_css
        mrp_workorder_view_kanban_inherit_quality
        action_{quality_mrp,mrp_workorder}_show_steps
        mrp_routing_view_form_inherit_quality
        mrp_workcenter_view_kanban_inherit_{quality_mrp,workorder}
        quality_point_view_form_inherit_mrp

        test_type_register_consumed_materials
        quality_point_component_registration
        quality_point_component_registration_2
        quality_point_4

    """)
    for m in moved:
        if '{' not in m:
            f, t = m, m
        else:
            f, t = util.expand_braces(m)
        util.rename_xmlid(cr, 'quality_mrp.' + f, 'mrp_workorder.' + t)

    moved2 = util.splitlines("""
        quality_alert_view_search_inherit_quality_mrp{,workorder}
        quality_check_view_form_inherit_mrp
        quality_alert_view_form_inherit_mrp
        quality_check_action_wo
    """)
    for m in moved2:
        if '{' not in m:
            f, t = m, m
        else:
            f, t = util.expand_braces(m)
        util.rename_xmlid(cr, 'quality_mrp.' + f, 'quality_mrp_workorder.' + t)

    cr.execute("""
        UPDATE ir_model_data
           SET module='quality_mrp_worker'
         WHERE module='quality_mrp'
           AND model IN ('quality.point.test_type',
                         'quality.point'
                        )
    """)

    # move fields
    # ===========

    fields_moved = {
        'quality.point': """
                failure_message
                measure_frequency_type measure_frequency_value
                measure_frequency_unit_value measure_frequency_unit
                norm tolerance_min tolerance_max norm_unit
                average standard_deviation
            """,
        'quality.check': """
                failure_message warning_message
                measure measure_success
                norm_unit tolerance_min tolerance_max
            """,
        'stock.picking': """
                check_ids quality_check_todo quality_check_fail
                quality_alert_ids quality_alert_count
            """,
    }

    for model, fields in fields_moved.items():
        for field in fields.split():
            util.move_field_to_module(cr, model, field, 'quality', 'quality_control')

    for f in 'measure measure_success norm_unit picture'.split():
        util.move_field_to_module(cr, 'mrp.workorder', f, 'mrp_workorder', 'quality_mrp_workorder')

    cr.execute("""
        UPDATE ir_model_data
           SET module='mrp_workorder'
         WHERE module='quality_mrp'
           AND model='ir.model.fields'
           AND res_id IN (SELECT id
                            FROM ir_model_fields
                           WHERE model IN ('quality.point.test_type',
                                           'quality.point',
                                           'quality.alert',
                                           'quality.check',
                                           'mrp.workorder')
                             AND name != 'production_id')
    """)
