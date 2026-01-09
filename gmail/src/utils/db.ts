import { Pool } from "pg";
import { PSQL_DB, PSQL_HOST, PSQL_PASS, PSQL_PORT, PSQL_USER } from "../consts";

const pool = new Pool({
    user: PSQL_USER,
    password: PSQL_PASS,
    database: PSQL_DB,
    host: PSQL_HOST,
    port: PSQL_PORT,
});

pool.on("error", (err, client) => {
    console.error("Could not connect to the database", err);
    process.exit(-1);
});

export default pool;
