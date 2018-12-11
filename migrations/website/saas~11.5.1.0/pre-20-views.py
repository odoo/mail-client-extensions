# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "website.layout")
    util.rename_xmlid(cr, 'website.menu_homepage','website.menu_home')
    """
    Ensure each website qweb view, and all their inherited views,
    have an XMLId and a key.
    """
    cr.execute("SELECT id FROM website ORDER BY id LIMIT 1")
    record = cr.fetchone()
    website_id = record[0] if record else False
    cr.execute(
        """
        SELECT v.id
        FROM ir_ui_view v INNER JOIN
           ir_model_data x ON (v.id = x.res_id AND x.model = 'ir.ui.view')
        WHERE x.module = 'website' and v.type='qweb'
          AND (v.inherit_id IS NULL or v.mode='primary');
    """
    )
    for view_id in [x[0] for x in cr.fetchall()]:
        assign_key_and_xmlid(cr, view_id, website_id)


def assign_key_and_xmlid(cr, view_id, website_id):
    """
    - Ensure an XML ID exist
    - Ensure the key is set
    - Search for all inherited views
    """
    cr.execute("SELECT id, module, name FROM ir_model_data WHERE model='ir.ui.view' and res_id=%s", (view_id,))

    record = cr.fetchone()
    if not record:
        cr.execute(
            """INSERT INTO ir_model_data
                                  (module, name, model, res_id, noupdate)
                           VALUES ('website_migration', %s, 'ir.ui.view', %s, FALSE)
                   """,
            ("qweb_view_%s" % view_id, view_id),
        )
        xml_id = "website_migration.qweb_view_{}".format(view_id)
    else:
        xml_id = "{}.{}".format(record[1], record[2])

    cr.execute("SELECT key FROM ir_ui_view WHERE id=%s", (view_id,))
    key = cr.fetchone()[0]
    if not key:
        key = xml_id
    cr.execute("UPDATE ir_ui_view SET key=%s,website_id=%s WHERE id=%s", (key, website_id, view_id))

    cr.execute(
        """
        SELECT v.id, x.module || '.' || x.name
        FROM ir_ui_view v LEFT JOIN
           ir_model_data x ON (v.id = x.res_id AND x.model = 'ir.ui.view' AND x.module !~ '^_')
        WHERE v.inherit_id = %s;
    """,
        [view_id],
    )
    for inherited_view_id in [x[0] for x in cr.fetchall()]:
        assign_key_and_xmlid(cr, inherited_view_id, website_id)
