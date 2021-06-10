# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.rename_model(cr, 'hr.equipment', 'maintenance.equipment')
    util.rename_model(cr, 'hr.equipment.category', 'maintenance.equipment.category')
    util.rename_model(cr, 'hr.equipment.stage', 'maintenance.stage')
    util.rename_model(cr, 'hr.equipment.request', 'maintenance.request')

    util.rename_field(cr, 'maintenance.request', 'active', 'archive')
    cr.execute("UPDATE maintenance_request SET archive=not archive")

    # to be fair, these changes should be part of script for `hr_maintenance` module
    # we know this new module will be installed due to previous deps of `hr_equipment` module.
    # but it is easier to have the migration script at one place.
    for m in 'equipment request'.split():
        model = 'maintenance.' + m
        table = util.table_of_model(cr, model)
        util.rename_field(cr, model, 'user_id', 'technician_user_id')
        util.create_column(cr, table, 'owner_user_id', 'int4')
        util.move_field_to_module(cr, model, 'employee_id', 'maintenance', 'hr_maintenance')
        util.move_field_to_module(cr, model, 'department_id', 'maintenance', 'hr_maintenance')

    util.move_field_to_module(cr, 'maintenance.equipment', 'equipment_assign_to',
                              'maintenance', 'hr_maintenance')
    cr.execute("""
        UPDATE maintenance_equipment m
           SET owner_user_id = r.user_id
          FROM hr_employee e, resource_resource r
         WHERE e.id = m.employee_id
           AND r.id = e.resource_id
           AND m.equipment_assign_to = 'employee'
    """)
    cr.execute("""
        UPDATE maintenance_equipment m
           SET owner_user_id = r.user_id
          FROM hr_department d, hr_employee e, resource_resource r
         WHERE d.id = m.department_id
           AND e.id = d.manager_id
           AND r.id = e.resource_id
           AND m.equipment_assign_to = 'department'
    """)
    cr.execute("""
        UPDATE maintenance_request m
           SET owner_user_id = r.user_id
          FROM maintenance_equipment eq, hr_employee e, resource_resource r
         WHERE eq.id = m.equipment_id
           AND e.id = m.employee_id
           AND r.id = e.resource_id
           AND eq.equipment_assign_to = 'employee'
    """)
    cr.execute("""
        UPDATE maintenance_request m
           SET owner_user_id = r.user_id
          FROM maintenance_equipment eq, hr_department d, hr_employee e, resource_resource r
         WHERE eq.id = m.equipment_id
           AND d.id = m.department_id
           AND e.id = d.manager_id
           AND r.id = e.resource_id
           AND eq.equipment_assign_to = 'department'
    """)

    # recreate records and access rules
    cr.execute("""
        UPDATE ir_model_data
           SET noupdate=false
         WHERE module='maintenance'
           AND model IN ('ir.rule', 'ir.model.access')
    """)
