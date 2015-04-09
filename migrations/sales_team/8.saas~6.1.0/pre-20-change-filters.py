# -*- coding: utf-8 -*-

def migrate(cr, version):
    # we don't filter on model. It's unlikely that someone create a column named `section_id`
    cr.execute("""
        UPDATE ir_filters
           SET domain = regexp_replace(domain, '\ysection_id\y', 'team_id', 'g'),
               context = regexp_replace(regexp_replace(context,
                                        '\ysection_id\y', 'team_id', 'g'),
                                        '\ydefault_section_id\y', 'default_section_id', 'g')
    """)

    # do the same on ir.exports.line
    cr.execute("""
        UPDATE ir_exports_line
           SET name = regexp_replace(name, '\ysection_id\y', 'team_id', 'g')
    """)
