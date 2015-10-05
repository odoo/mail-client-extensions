# -*- coding: utf-8 -*-
"""
    Fixup m2m tables that have been generated without FK by previous migration scripts.
    See https://github.com/odoo/saas-migration/commit/d072c67b89ab468f6da3cf858b987622d8522a2f
"""
import logging
from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.base.9.'
_logger = logging.getLogger(NS + __name__)

def target_of(cr, table, column):
    cr.execute("""
        SELECT con.conname, cl2.relname, att2.attname
          FROM pg_constraint con
          JOIN pg_class cl1 ON (con.conrelid = cl1.oid)
          JOIN pg_attribute att1 ON (    array_lower(con.conkey, 1) = 1
                                     AND con.conkey[1] = att1.attnum
                                     AND att1.attrelid = cl1.oid)
          JOIN pg_class cl2 ON (con.confrelid = cl2.oid)
          JOIN pg_attribute att2 ON (    array_lower(con.confkey, 1) = 1
                                     AND con.confkey[1] = att2.attnum
                                     AND att2.attrelid = cl2.oid)
         WHERE cl1.relname = %s
           AND att1.attname = %s
           AND con.contype = 'f'
    """, [table, column])
    return cr.fetchone()


def fixup_m2m(cr, m2m, fk1, fk2, col1=None, col2=None):
    if col1 is None:
        col1 = '%s_id' % fk1
    if col2 is None:
        col2 = '%s_id' % fk2

    if not util.table_exists(cr, m2m):
        return

    # cleanup
    cr.execute("""
        DELETE FROM {m2m} t
              WHERE {col1} IS NULL
                 OR {col2} IS NULL
                 OR NOT EXISTS (SELECT id FROM {fk1} WHERE id=t.{col1})
                 OR NOT EXISTS (SELECT id FROM {fk2} WHERE id=t.{col2})
    """.format(**locals()))
    deleted = cr.rowcount
    if deleted:
        _logger.debug("%(m2m)s: removed %(deleted)d invalid rows", locals())

    # remove duplicated rows
    cr.execute("""
        DELETE FROM {m2m}
              WHERE ctid IN (SELECT ctid
                               FROM (SELECT ctid,
                                            ROW_NUMBER() OVER (PARTITION BY {col1}, {col2}
                                                                   ORDER BY ctid) as rnum
                                       FROM {m2m}) t
                              WHERE t.rnum > 1)
    """.format(**locals()))
    deleted = cr.rowcount
    if deleted:
        _logger.debug("%(m2m)s: removed %(deleted)d duplicated rows", locals())

    # set not null
    cr.execute("ALTER TABLE {m2m} ALTER COLUMN {col1} SET NOT NULL".format(**locals()))
    cr.execute("ALTER TABLE {m2m} ALTER COLUMN {col2} SET NOT NULL".format(**locals()))

    # create  missing or bad fk
    target = target_of(cr, m2m, col1)
    if target and target[1:] != [fk1, 'id']:
        cr.execute("ALTER TABLE {m2m} DROP CONSTRAINT {con}".format(m2m=m2m, con=target[0]))
        target = None
    if not target:
        _logger.debug("%(m2m)s: add FK %(col1)s -> %(fk1)s", locals())
        cr.execute("ALTER TABLE {m2m} ADD FOREIGN KEY ({col1}) REFERENCES {fk1} ON DELETE CASCADE"
                   .format(**locals()))

    target = target_of(cr, m2m, col2)
    if target and target[1:] != [fk2, 'id']:
        cr.execute("ALTER TABLE {m2m} DROP CONSTRAINT {con}".format(m2m=m2m, con=target[0]))
        target = None
    if not target:
        _logger.debug("%(m2m)s: add FK %(col2)s -> %(fk2)s", locals())
        cr.execute("ALTER TABLE {m2m} ADD FOREIGN KEY ({col2}) REFERENCES {fk2} ON DELETE CASCADE"
                   .format(**locals()))

    # create indexes
    idx = util.get_index_on(cr, m2m, col1, col2)
    if not idx or not idx[1]:
        cr.execute("CREATE UNIQUE INDEX ON %s (%s, %s)" % (m2m, col1, col2))

    if not util.get_index_on(cr, m2m, col1):
        cr.execute('CREATE INDEX ON "%s" ("%s")' % (m2m, col1))
    if not util.get_index_on(cr, m2m, col2):
        cr.execute('CREATE INDEX ON "%s" ("%s")' % (m2m, col2))

def migrate(cr, version):
    # cmr@saas-6
    fixup_m2m(cr, 'crm_lead_tag_rel', 'crm_lead', 'crm_lead_tag', 'lead_id', 'tag_id')
    fixup_m2m(cr, 'sale_order_tag_rel', 'sale_order', 'crm_lead_tag', 'order_id', 'tag_id')

    # ignore it, this table has not been migrated in 8.0 -> drop it (nobody complain, must not be very important)
    # fixup_m2m(cr, "im_session_im_user_rel", "im_session", "im_user")
    for tbl in "im_message_users im_session_im_user_rel im_message im_session im_user".split():
        cr.execute("DROP TABLE IF EXISTS " + tbl)

    # point_of_sale@saas-6
    fixup_m2m(cr, 'account_tax_pos_order_line_rel', 'pos_order_line', 'account_tax')

    # producte@saas-5
    fixup_m2m(cr, 'product_attribute_value_product_product_rel',
              'product_attribute_value', 'product_product', 'att_id', 'prod_id')
    fixup_m2m(cr, 'product_attribute_line_product_attribute_value_rel',
              'product_attribute_line', 'product_attribute_value', 'line_id', 'val_id')

    # purchase_requistion@saas-6
    fixup_m2m(cr, 'purchase_requisition_supplier_rel',
              'purchase_requisition_partner', 'res_partner', 'requisition_id', 'partner_id')

    # website_sale@saas-5
    fixup_m2m(cr, 'product_public_category_product_template_rel',
              'product_template', 'product_public_category')
