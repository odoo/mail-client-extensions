# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("SELECT active FROM ir_rule WHERE id = %s", [util.ref(cr, "base.res_partner_rule")])
    if not cr.rowcount or not cr.fetchone()[0]:
        # loutish technique to set a column to NULL
        # it's also O(1) instead of O(n) with an UPDATE
        util.remove_column(cr, "res_partner", "company_id")
        util.create_column(cr, "res_partner", "company_id", "int4")

    cr.execute("ALTER TABLE ir_model_data ALTER COLUMN noupdate SET DEFAULT false")

    util.move_model(cr, "report.layout", "web", "base")
    util.create_column(cr, "report_layout", "name", "varchar")
    cr.execute("UPDATE report_layout l SET name = v.name FROM ir_ui_view v WHERE v.id = l.view_id")

    util.remove_field(cr, "ir.actions.act_window", "view_type")
    util.remove_column(cr, "ir_attachment", "res_name")  # non-stored computed field

    util.remove_field(cr, "ir.model.constraint", "date_update")
    util.remove_field(cr, "ir.model.relation", "date_update")
    util.update_field_references(
        cr, "date_update", "write_date", only_models=("ir.model.constraint", "ir.model.relation")
    )
    util.remove_field(cr, "ir.model.constraint", "date_init")
    util.remove_field(cr, "ir.model.relation", "date_init")
    util.update_field_references(
        cr, "date_init", "create_date", only_models=("ir.model.constraint", "ir.model.relation")
    )

    util.remove_field(cr, "ir.translation", "source")
    util.update_field_references(cr, "source", "src", only_models=("ir.translation",))

    util.create_column(cr, "res_company", "font", "varchar")
    util.create_column(cr, "res_company", "primary_color", "varchar")
    util.create_column(cr, "res_company", "secondary_color", "varchar")
    cr.execute("UPDATE res_company SET font = 'Lato'")

    util.remove_field(cr, "res.lang", "translatable")
    util.create_column(cr, "res_lang", "url_code", "varchar")
    cr.execute("UPDATE res_lang SET url_code = code")

    util.remove_module_deps(cr, 'saas_docsaway', ('print_docsaway',))
    util.remove_module(cr, 'saas_docsaway')

    util.parallel_execute(cr, util.explode_query(cr, "UPDATE ir_model_data SET noupdate=TRUE WHERE noupdate IS NULL"))

    if util.module_installed(cr, "test_new_api"):
        util.move_model(cr, "decimal.precision.test", "base", "test_new_api")
    else:
        util.remove_model(cr, "decimal.precision.test")
