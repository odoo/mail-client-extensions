import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { State } from "../models/state";

/**
 * Log the given email body in the chatter of the given record.
 */
export function logEmail(recordId: number, recordModel: string, emailBody: string): boolean {
    const url = State.odooServerUrl + URLS.LOG_EMAIL;
    const accessToken = State.accessToken;

    const response = postJsonRpc(
        url,
        { message: emailBody, res_id: recordId, model: recordModel },
        { Authorization: "Bearer " + accessToken },
    );
    return !!response;
}
