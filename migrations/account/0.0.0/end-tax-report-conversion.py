# -*- coding: utf-8 -*-

# (Hopefully) the Philosopher's Stone for tax reports
# This script defines a generic way of converting a tax report into its new
# version when it got deprecated in Odoo. All the conversion relies on
# a mapping between both reports, that needs to be provided in the corresponding
# localization module.

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.table_exists(cr, "account_tax_report_conversion_map"):
        # This temporary table is used to pass the report lines to convert.
        # It is created when trying to append elements to it. So, there is nothing
        # to do if it does not exist.
        return

    env = util.env(cr)

    cr.execute("""
        SELECT *
        FROM account_tax_report_conversion_map
    """)

    for mapping in cr.dictfetchall():
        line_from = env.ref(mapping["module"] + "." + mapping["from_xmlid"])
        line_to = env.ref(mapping["module"] + "." + mapping["to_xmlid"])

        for from_tag in line_from.tag_ids:
            needs_neg_tag = not from_tag.tax_negate if mapping["invert_tag_sign"] else from_tag.tax_negate
            to_tag = line_to.tag_ids.filtered(lambda x, needs_neg_tag=needs_neg_tag: x.tax_negate == needs_neg_tag)

            query_params = {"from_tag": from_tag.id, "to_tag": to_tag.id}
            # Update tax repartion lines
            tax_rep_query = """
                UPDATE account_account_tag_account_tax_repartition_line_rel
                SET account_account_tag_id = %(to_tag)s
                WHERE account_account_tag_id = %(from_tag)s
            """
            if mapping["tax_rep_condition"]:
                tax_rep_query += "AND " + mapping["tax_rep_condition"]

            cr.execute(tax_rep_query, query_params)

            # Update account move lines
            aml_query = """
                UPDATE account_account_tag_account_move_line_rel
                SET account_account_tag_id = %(to_tag)s
                WHERE account_account_tag_id = %(from_tag)s
            """
            if mapping["aml_condition"]:
                aml_query += "AND " + mapping["aml_condition"]

            cr.execute(aml_query, query_params)

    cr.execute(
        """
        SELECT array_agg(account_tax_report_line.id)
        FROM account_tax_report_line
        JOIN ir_model_data data
            ON data.id = account_tax_report_line.id
            AND data.module = %(module)s
            AND data.name = %(data_name)s
    """,
        {
            "module": mapping["module"],
            "data_name": mapping["from_xmlid"],
        },
    )

    # Unlink instead of SQL delete as it will also perform some logic on the tags
    # linked to the report line in 13.1+, unlinking them as well only if they
    # are not used by some other report. Indeed, tags can be shared between multiple
    # reports. If they need to be split instead of all converted, additional
    # conditions and treatment through options on taxes and amls will be required.
    to_unlink_ids = cr.fetchone()[0]
    env["account.tax.report.line"].browse(to_unlink_ids).unlink()

    # We don't remove the account.tax.report in 13.1+ here; we consider it is kept, only its lines change.

    # Delete migration table
    cr.execute("""
        DROP TABLE account_tax_report_conversion_map
    """)


def init_tax_report_conversion(cr, module_name, mapping_list):
    """Marks tax report as needing a conversion following the provided mapping.
    This helper function must be called in pre in localization modules, so that
    the actual conversion gets automatically performed in end of account module.

    :param module_name:  The module we want to convert the tax report from
    :param mapping_list: A list of tuples giving the mapping between old and new
                         report lines. Each of these tuples consist minimum 2 and
                         maximum 3 elements, as follows:
                            Index 0: the xmlid (without module name) of the old report line
                            Index 1: the xmlid (without module name) of the new report line
                            Index 2 (optional): options, as a dictionary.
                                Authorized options are:
                                - 'account.move.line': an additional SQL condition to apply to move lines when
                                                       replacing the tags corresponding to the associated mapping
                                - 'account.tax':       an additional SQL condition to apply to taxes when
                                                       replacing the tags corresponding to the associated mapping
                                - 'invert_tag_sign':   whether or not + sign of old line corresponds to - sign of new line
    """
    if not util.version_gte("saas~12.3"):
        # We can add support for other versions if we need it.
        raise NotImplementedError("Tax report conversion helper is only available for 12.3 and higher.")

    if not util.table_exists(cr, "account_tax_report_conversion_map"):
        cr.execute("""
            CREATE TABLE account_tax_report_conversion_map (
                module VARCHAR NOT NULL,
                from_xmlid VARCHAR NOT NULL,
                to_xmlid VARCHAR NOT NULL,
                aml_condition VARCHAR,
                tax_rep_condition VARCHAR,
                invert_tag_sign BOOLEAN
            )
        """)

    for mapping in mapping_list:
        options = (len(mapping) > 2 and mapping[2]) or {}

        query_params = (
            module_name,
            mapping[0],
            mapping[1],
            options.get("account.move.line", None),
            options.get("account.tax", None),
            options.get("invert_tag_sign"),
        )

        cr.execute(
            """
            INSERT INTO account_tax_report_conversion_map
            VALUES %s
        """,
            (query_params,),
        )

    # We now want to mark the data to convert as noupdate, so that they are
    # still there in post and can be used to actually do the conversion.
    # They will have to be deleted explicitly in end when we don't need them anymore.
    cr.execute("""
        UPDATE ir_model_data data
        SET noupdate = true
        FROM account_tax_report_conversion_map conv_map
        WHERE data.module = conv_map.module
        AND data.name = conv_map.from_xmlid
    """)
