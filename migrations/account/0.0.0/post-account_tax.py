from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("15.0", "18.0"):
        cr.execute(
            """
            WITH RECURSIVE _deleted_rels AS (
                DELETE FROM account_tax_filiation_rel rel
                 USING account_tax child_tax
                 WHERE child_tax.id = rel.child_tax
                   AND child_tax.amount_type = 'group'
             RETURNING rel.parent_tax, rel.child_tax
            ),
            _last_children_rel AS (
                    -- start with all taxes that have at least one group child
                SELECT cte.parent_tax AS root,
                       cte.child_tax AS child,
                       False AS is_child_leaf
                  FROM _deleted_rels cte
                 UNION
                    -- add further children of *only* group taxes
                SELECT tree.root,
                       child_tax.id AS child,
                       child_tax.amount_type != 'group' AS is_child_leaf
                  FROM _last_children_rel tree
                  JOIN account_tax_filiation_rel rel
                    ON rel.parent_tax = tree.child
                  JOIN account_tax child_tax
                    ON child_tax.id = rel.child_tax
                 WHERE NOT tree.is_child_leaf
            )
            INSERT INTO account_tax_filiation_rel(parent_tax, child_tax)
            SELECT root, child
              FROM _last_children_rel
             WHERE is_child_leaf
       ON CONFLICT (parent_tax, child_tax) DO NOTHING
            """
        )
