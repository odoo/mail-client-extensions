# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("SELECT demo FROM ir_module_module WHERE name='base'")
    demo = cr.fetchone()[0]
    if not demo:
        return

    # If we are in demo mode, the `warehouse0` should have the field `{in,out}_type_id` set *before* loading the data files
    # This field is normally fill by the `post-10-warehouseconf.py` file by the call to `create_sequences_and_picking_types`.
    # For demo data, this is too late. So we fill this column with dumb data
    # Just to be clear, this is NOT breaking customer upgrades, only the CI tests.
    cr.execute(
        """
            CREATE TABLE stock_picking_type(
                id SERIAL NOT NULL PRIMARY KEY,
                name varchar
            )
        """
    )
    cr.execute("INSERT INTO stock_picking_type(name) VALUES('in'), ('out') RETURNING id")
    spt_in, spt_out = [spt for spt, in cr.fetchall()]

    cr.execute("UPDATE stock_warehouse SET in_type_id=%s, out_type_id=%s", [spt_in, spt_out])
