def prepare_migration(cr):
    # No need to raise an error and stop the upgrade if the record is a parent of itself
    cr.execute("UPDATE res_partner SET parent_id = NULL WHERE parent_id = id")

    # check there are no cycles in partners hierarchy this is not allowed by standard
    # BUT if there is a cycle some computed fields may end up in an infinite loop
    cr.execute(
        """
        WITH RECURSIVE info AS (
            SELECT parent_id AS id,
                   ARRAY[parent_id] AS path,
                   False AS cycle
              FROM res_partner
             WHERE parent_id IS NOT NULL
             GROUP BY parent_id

             UNION ALL

            SELECT child.id AS id,
                   ARRAY_PREPEND(child.id, parent.path) AS path,
                   child.id =ANY(parent.path) AS cycle
              FROM info AS parent
              JOIN res_partner child
                ON child.parent_id = parent.id
             WHERE NOT parent.cycle
        )
        SELECT path FROM info WHERE cycle
       """
    )

    if cr.rowcount:
        # extract the cycle for each path and put it in a summary to report
        res = []
        done = set()
        for (path,) in cr.fetchall():
            if set(path) & done:  # cycle in path already in the summary
                continue
            res.append(path[: path.index(path[0], 1) + 1])  # add only the cycle part in path
            done.update(path)  # all partners in this path already had the cycle identified
        report = "\n".join((" * " + "->".join("res.partner({})".format(id_) for id_ in path)) for path in res)
        raise ValueError("Cycle detected for the following partners (via `parent_id`):\n{}".format(report))
