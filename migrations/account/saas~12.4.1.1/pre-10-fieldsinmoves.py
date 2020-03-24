# -*- coding: utf-8 -*-


def migrate(cr, version):
    """
    Copy fields from account.invoice to account.move (lines also)
    Just store fields definition (as the model will be dropped in next script)
    And used in post-script when link invoice<->move is available

    To avoid field definition loose, custom fields should also be adapted
    """
    cr.execute(
        """
    CREATE TABLE mig_s124_accountfieldstotransfer (
        name varchar,
        ttype varchar,
        src_model varchar,
        dst_model varchar,
        state varchar,
        transfer boolean DEFAULT FALSE
    )
    """
    )
    for suffix in ["", ".line"]:
        src_model = "account.invoice%s" % suffix
        dst_model = "account.move%s" % suffix

        cr.execute(
            """
            INSERT INTO mig_s124_accountfieldstotransfer (name,ttype,src_model,dst_model,state)
            SELECT f.name, ttype, %s as src_model, %s as dst_model, f.state
              FROM ir_model_fields f
        INNER JOIN ir_model m on f.model_id=m.id
             WHERE m.model=%s
               AND f.store=TRUE
               AND f.name not in (
                  SELECT f2.name
                    FROM ir_model_fields f2
              INNER JOIN ir_model m2 on f2.model_id=m2.id
                   WHERE m2.model=%s
                     AND f2.store=TRUE
               )
            """,
            [src_model, dst_model, src_model, dst_model],
        )
