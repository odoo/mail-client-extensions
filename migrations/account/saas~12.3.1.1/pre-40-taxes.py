# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # These two tables are used to migrate financial tags ; they can be filled in
    # pre script by l10n modules if needed (see l10n_es for an example)
    cr.execute(
        """
        CREATE TABLE financial_tags_conversion_map(
            old_tag_name VARCHAR,
            new_tag_name VARCHAR,
            invoice_type VARCHAR,
            repartition_type VARCHAR,
            module VARCHAR
        );
    """
    )

    cr.execute(
        """
        CREATE TABLE v12_financial_tags_registry(
            tag_id INTEGER REFERENCES account_account_tag(id))
    """
    )

    # This table is used to store the group taxes that should not be merged with their children
    # into a single tax
    cr.execute(
        """
        CREATE TABLE taxes_not_to_merge(
            tax_id INTEGER REFERENCES account_tax(id)
        );
    """
    )
