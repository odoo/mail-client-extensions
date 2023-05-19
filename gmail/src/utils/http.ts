import { State } from "../models/state";

/**
 * Make a JSON RPC call with the following parameters.
 */
export function postJsonRpc(url: string, data = {}, headers = {}, options: any = {}) {
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
    } catch {
        return;
    }
}

/**
 * Make a JSON RPC call with the following parameters.
 *
 * Try to first read the response from the cache, if not found,
 * make the call and cache the response.
 *
 * The cache key is based on the URL and the JSON data
 *
 * Store the result for 6 hours by default (maximum cache duration)
 *
 * This cache may be needed to make to many HTTP call to an external service (e.g. IAP).
 */
export function postJsonRpcCached(url: string, data = {}, headers = {}, cacheTtl: number = 21600) {
    const cache = CacheService.getUserCache();

    // Max 250 characters, to hash the key to have a fixed length
    const cacheKey =
        "ODOO_HTTP_CACHE_" +
        Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, JSON.stringify([url, data])));

    const cachedResponse = cache.get(cacheKey);

    if (cachedResponse) {
        return JSON.parse(cachedResponse);
    }

    const response = postJsonRpc(url, data, headers);

    if (response) {
        cache.put(cacheKey, JSON.stringify(response), cacheTtl);
    }

    return response;
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
