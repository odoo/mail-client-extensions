# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("DROP TABLE ir_config_parameter_groups_rel")
    util.remove_field(cr, 'ir.config_parameter', 'group_ids')

    util.remove_field(cr, 'res.company', 'custom_footer')
    util.remove_field(cr, 'res.company', 'rml_footer_readonly')

    util.create_column(cr, 'res_partner', 'commercial_partner_country_id', 'int4')
    cr.execute("""
        UPDATE res_partner p
           SET commercial_partner_country_id = c.country_id
          FROM res_partner c
         WHERE c.id = p.commercial_partner_id
    """)

    models = util.splitlines("""
        ir.needaction_mixin

        workflow
        workflow.activity
        workflow.transition
        workflow.instance
        workflow.workitem
        workflow.triggers
    """)
    for model in models:
        util.delete_model(cr, model)

    # cleanup too-open security rules
    rules = util.splitlines("""
        access_ir_model_all
        access_ir_model_constraint
        access_ir_model_relation
        access_ir_model_access_all
        access_ir_model_data_all
        access_ir_model_fields_all
        access_ir_rule_group_user
        access_ir_filter all        # the space in the xmlid is really there...
        access_ir_config_parameter
        ir_config_parameter_rule
    """)

    for r in rules:
        util.remove_record(cr, 'base.' + r)
