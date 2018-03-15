# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def field_ref(cr, model, name):
    ref = util.IMD_FIELD_PATTERN % (model.replace('.', '_'), name)
    return util.ref(cr, 'hr.' + ref)

def migrate(cr, version):
    util.replace_record_references(
        cr,
        ('ir.model.fields', field_ref(cr, 'hr.employee', 'name')),
        ('ir.model.fields', field_ref(cr, 'hr.employee', 'name_related')),
        replace_xmlid=False,
    )
    cr.execute("SELECT id FROM ir_model_fields WHERE model='hr.employee' AND name='name'")
    if cr.rowcount:
        util.remove_record(cr, ('ir.model.fields', cr.fetchone()[0]))
    util.rename_field(cr, 'hr.employee', 'name_related', 'name')

    util.remove_field(cr, 'hr.employee', 'login')
    util.remove_field(cr, 'hr.employee', 'last_login')

    util.create_column(cr, 'hr_employee', 'company_id', 'int4')
    util.create_column(cr, 'hr_employee', 'active', 'boolean')
    cr.execute("""
        UPDATE hr_employee e
           SET company_id= r.company_id,
               active = r.active
          FROM resource_resource r
         WHERE r.id = e.resource_id
    """)
