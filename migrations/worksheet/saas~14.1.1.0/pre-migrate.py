# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        'industry_fsm_report.project_worksheet_template_view_search',
        'worksheet.worksheet_template_view_search'
    )
    util.rename_xmlid(
        cr,
        'industry_fsm_report.project_worksheet_template_view_list',
        'worksheet.worksheet_template_view_list'
    )
    util.rename_xmlid(
        cr,
        'industry_fsm_report.project_worksheet_template_view_form',
        'worksheet.worksheet_template_view_form'
    )
    util.rename_xmlid(
        cr,
        'industry_fsm_report.ir_rule_project_worksheet_template_multi_company',
        'worksheet.ir_rule_worksheet_template_multi_company'
    )
    util.rename_model(cr, "project.worksheet.template", "worksheet.template")
    util.move_model(cr, "worksheet.template", "industry_fsm_report", "worksheet")

    # add res_model_id to worksheet_template
    util.create_column(cr, "worksheet_template", "res_model_id", "int4")
    cr.execute(
        """
UPDATE worksheet_template
   SET res_model_id = (SELECT id
                         FROM ir_model
                        WHERE model = 'project.task');
        """
    )

    # change x_task_id to x_project_task_id
    cr.execute("SELECT im.model FROM ir_model im JOIN worksheet_template wt ON im.id = wt.model_id GROUP BY im.model")
    for (model,) in cr.fetchall():
        util.rename_field(cr, model, 'x_task_id', 'x_project_task_id')

    # change view arch for x_task_id
    cr.execute(
        r"""
UPDATE ir_ui_view
   SET arch_db = regexp_replace(regexp_replace(arch_db,
                                               '\yx_task_id\y', 'x_project_task_id', 'g'),
                                               '\ydefault_x_task_id\y', 'default_x_project_task_id', 'g')
 WHERE model IN (SELECT im.model
                   FROM ir_model im
                        JOIN worksheet_template wt
                          ON im.id = wt.model_id);
        """
    )
