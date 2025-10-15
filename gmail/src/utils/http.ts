import { State } from "../models/state";

/**
 * Make a JSON RPC call with the following parameters.
 */
export function postJsonRpc(url: string, data = {}, headers = {}, options: any = {}) {
    for (const key in data) {
        // don't send null values
        if (data[key] === undefined || data[key] === null) {
            data[key] = false;
        }
    }

    // Make a valid "Odoo RPC" call
    data = {
        id: 0,
        jsonrpc: "2.0",
        method: "call",
        params: data,
    };

    const httpOptions = {
        method: "post" as GoogleAppsScript.URL_Fetch.HttpMethod,
        contentType: "application/json",
        payload: JSON.stringify(data),
        headers: headers,
    };

    try {
        const response = UrlFetchApp.fetch(url, httpOptions);

        if (options.returnRawResponse) {
            return response;
        }

        const responseCode = response.getResponseCode();

        if (responseCode > 299 || responseCode < 200) {
            return;
        }

        const textResponse = response.getContentText("UTF-8");
        const dictResponse = JSON.parse(textResponse);

        if (!dictResponse.result) {
            return;
        }

        return dictResponse.result;
    } catch (e) {
        Logger.log(`HTTP Error: ${e}`);
        return;
    }
}

/**
 * Take a dictionary and return the URL encoded parameters
 */
export function encodeQueryData(parameters: Record<string, string>): string {
    const queryParameters = [];
    for (let key in parameters) {
        queryParameters.push(encodeURIComponent(key) + "=" + encodeURIComponent(parameters[key]));
    }
    return "?" + queryParameters.join("&");
}
