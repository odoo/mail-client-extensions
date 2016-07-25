# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    util.remove_view(cr, 'openerp_website.openerp_website_change_pack')
    util.remove_view(cr, view_id=7341)

    cr.execute("""
        UPDATE res_country_state SET name='Victoria' WHERE id=246;
        UPDATE res_country_state SET name='Distrito Federal' WHERE id=144;
        UPDATE res_country_state SET name='Tasmania', code='TAS' WHERE id=370;
        UPDATE res_country_state SET name='New South Wales', code='NSW' WHERE id=375;
        UPDATE res_country_state SET code='42' WHERE id=410;
        UPDATE res_country_state SET code='31' WHERE id=381;
        UPDATE res_country_state SET code='32' WHERE id=311;
        UPDATE res_country_state SET name='Shandong', code='37' WHERE id IN (328, 494);
        UPDATE res_country_state SET name='Guangdong', code='44' WHERE id IN (309, 320, 405);
        UPDATE res_country_state SET name='Jawa Timur', code='JI' WHERE id IN (277, 279);

        UPDATE res_country_state SET name='Hong Kong', code='HK' WHERE country_id = 92;
    """)

    # add missing fk + cleaning what should have been nullified or deleted
    for column in 'create_uid write_uid user_id'.split():
        cr.execute("""
            UPDATE openerp_enterprise_database_user du
               SET {column} = NULL
             WHERE {column} IS NOT NULL
               AND NOT EXISTS(SELECT 1 FROM res_users WHERE id = du.{column})
        """.format(column=column))
        cr.execute("""
            ALTER TABLE openerp_enterprise_database_user
        ADD FOREIGN KEY ({column}) REFERENCES res_users ON DELETE set null
        """.format(column=column))

    cr.execute("""
        DELETE FROM openerp_enterprise_database_user du
              WHERE NOT EXISTS(SELECT 1 FROM openerp_enterprise_database WHERE id = du.database_id)
    """)
    cr.execute("""
        ALTER TABLE openerp_enterprise_database_user
    ADD FOREIGN KEY (database_id) REFERENCES openerp_enterprise_database ON DELETE cascade
    """.format(column=column))

def _altamotors_remove_specific_view(cr, version):
    util.remove_view(cr, view_id=918)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
        'a79ed906-32e4-406b-ab62-6bba74d96994': _altamotors_remove_specific_view,
        '8e24f066-fd2e-44a4-8962-dc73d793fc96': _altamotors_remove_specific_view, #Backup alta (jco)
    })
