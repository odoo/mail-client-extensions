# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def _openerp(cr, version):
    # remove invalid row that forbid creation of notnull constraint and index
    cr.execute("DELETE FROM ir_ui_view_custom WHERE ref_id IS NULL")

    # cleanup country states
    cr.execute("UPDATE res_country_state SET code='NT' WHERE id=1128")  # Hong Kong New Territories
    states = {
        1139: 1070,     # Uttar Pradesh
        1225: 166,      # Distrito Capital
        181: 545,       # Pará
        1151: 1049,     # Haryana
        1134: 1040,     # Assam
        1126: 88,       # Massachusetts
        1136: 1067,     # Tamil Nadu
        215: 1186,      # Atlántico
        1148: 949,      # Colima
    }
    for f, t in states.items():
        util.replace_record_references(cr, ('res.country.state', f), ('res.country.state', t))
        util.remove_record(cr, ('res.country.state', f))

    # remove invalid currencies
    cr.execute("DELETE FROM res_currency_rate WHERE currency_id IN (78,90,145,175)")
    cr.execute("DELETE FROM res_currency WHERE id IN (78,90,145,175)")

    cr.execute("UPDATE account_chart_template SET currency_id=1")

    # res.partner.bank
    cr.execute("DELETE FROM res_partner_bank WHERE acc_number IS NULL")
    cr.execute("DELETE FROM res_partner_bank WHERE id IN (289)")    # duplicate and suspicious
    pbanks = {
        17: 121,
        1989: 266,      # OpenERP Luxembourg
        1677: 1806,
        309: 189,
        61: 993,        # Garage Piret S.A.
        2014: 358,      # Hagrid SPRL
        102: 872,       # Petignot et fils
        286: 82,
        65: 83,
        1342: 150,      # OpenERP Inc.
        2139: 1160,     # Ferme de Bertinchamps SA
        2028: 896,
        994: 976,
        2015: 500,
        2693: 942,      # O'Labs
        2738: 2233,

        # OpenERP S.A. / ING
        1167: 244,
        1134: 244,
        1492: 244,
        1128: 244,
    }
    for f, t in pbanks.items():
        util.replace_record_references(cr, ('res.partner.bank', f), ('res.partner.bank', t))
        util.remove_record(cr, ('res.partner.bank', f))

    # duplicated barcode
    cr.execute("UPDATE product_product SET barcode=NULL WHERE barcode IS NOT NULL")

    cr.execute("""
        UPDATE account_analytic_line l
           SET name = t.name
          FROM product_product p JOIN product_template t ON (t.id = p.product_tmpl_id)
         WHERE p.id = l.product_id
           AND l.name IS NULL
    """)
    cr.execute("UPDATE account_analytic_line SET name='/' WHERE name IS NULL")

    # ping cleanup
    cr.execute("UPDATE openerp_enterprise_database SET language=language_moved0 WHERE language IS NULL")
    cr.execute("ALTER TABLE openerp_enterprise_database DROP COLUMN language_moved0")
    cr.execute("""
        UPDATE openerp_enterprise_ping p
           SET language = COALESCE(d.language, 'en_US')
          FROM openerp_enterprise_database d
         WHERE d.id = p.database
           AND p.language IS NULL
    """)
    cr.execute("""
        UPDATE openerp_enterprise_ping p
           SET db_name = COALESCE(d.db_name, d.db_uuid)
          FROM openerp_enterprise_database d
         WHERE d.id = p.database
           AND p.db_name IS NULL
    """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _openerp,
    })
