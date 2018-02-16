# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.delete_model(cr, 'res.font')
    util.delete_model(cr, 'base.module.configuration')

    util.remove_field(cr, 'ir.actions.todo', 'type')
    util.remove_field(cr, 'ir.actions.todo', 'note')
    util.remove_field(cr, 'ir.actions.todo', 'groups_id')
    cr.execute("DROP TABLE res_groups_action_rel")

    util.rename_field(cr, 'res.company', 'rml_header1', 'report_header')
    util.rename_field(cr, 'res.company', 'rml_footer', 'report_footer')

    for field in 'rml_header rml_header2 rml_header3 font fax rml_paper_format'.split():
        util.remove_field(cr, 'res.company', field)

    util.create_column(cr, 'res_country', 'name_position', 'varchar')
    cr.execute("UPDATE res_country SET name_position='before'")
    cr.execute("UPDATE res_country SET name_position='after' WHERE id=%s",
               [util.ref(cr, 'base.jp')])

    # ir.values,value text -> binary
    cr.execute("SELECT character_set_name FROM information_schema.character_sets")
    charset, = cr.fetchone()
    cr.execute("""
         ALTER TABLE ir_values ALTER COLUMN "value" TYPE bytea USING convert_to("value", '{0}')
    """.format(charset))
    delattr(util._ir_values_value, 'result')
