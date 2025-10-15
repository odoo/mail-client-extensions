import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { ErrorMessage } from "../models/error_message";
import { _t } from "../services/translation";
import { getAccessToken } from "./odoo_auth";

/**
 * Search records of the given model.
 */
export function searchRecords(recordModel: string, query: string): [any[], number, ErrorMessage] {
    const odooAccessToken = getAccessToken();
    const url =
        PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
        URLS.SEARCH_RECORDS +
        "/" +
        recordModel;

    const response = postJsonRpc(url, { query }, { Authorization: "Bearer " + odooAccessToken });

    if (!response?.length) {
        return [[], 0, new ErrorMessage("unknown", response.error)];
    }

    return [response[0], response[1], new ErrorMessage(null)];
}
