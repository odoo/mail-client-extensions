import { URLS } from "../consts";
import { ErrorMessage } from "../models/error_message";
import { User } from "../models/user";
import { postJsonRpc } from "../utils/http";

/**
 * Search records of the given model.
 */
export async function searchRecords(
    user: User,
    recordModel: string,
    query: string,
): Promise<[any[], number, ErrorMessage]> {
    const response = await postJsonRpc(
        user.odooUrl + URLS.SEARCH_RECORDS + "/" + recordModel,
        { query },
        { Authorization: "Bearer " + user.odooToken },
    );

    if (!response?.length) {
        return [[], 0, new ErrorMessage("unknown", response.error)];
    }

    return [response[0], response[1], new ErrorMessage(null)];
}
