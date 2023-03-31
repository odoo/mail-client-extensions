/**
 * Make a JSON RPC call with the following parameters.
 */
function postJsonRpc(url, data, headers, options) {
    if (data === void 0) {
        data = {};
    }
    if (headers === void 0) {
        headers = {};
    }
    if (options === void 0) {
        options = {};
    }
    // Make a valid "Odoo RPC" call
    data = {
        id: 0,
        jsonrpc: "2.0",
        method: "call",
        params: data,
    };
    var httpOptions = {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(data),
        headers: headers,
    };
    try {
        var response = UrlFetchApp.fetch(url, httpOptions);
        if (options.returnRawResponse) {
            return response;
        }
        var responseCode = response.getResponseCode();
        if (responseCode > 299 || responseCode < 200) {
            return;
        }
        var textResponse = response.getContentText("UTF-8");
        var dictResponse = JSON.parse(textResponse);
        if (!dictResponse.result) {
            return;
        }
        return dictResponse.result;
    } catch (_a) {
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
function postJsonRpcCached(url, data, headers, cacheTtl) {
    if (data === void 0) {
        data = {};
    }
    if (headers === void 0) {
        headers = {};
    }
    if (cacheTtl === void 0) {
        cacheTtl = 21600;
    }
    var cache = CacheService.getUserCache();
    // Max 250 characters, to hash the key to have a fixed length
    var cacheKey =
        "ODOO_HTTP_CACHE_" +
        Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, JSON.stringify([url, data])));
    var cachedResponse = cache.get(cacheKey);
    if (cachedResponse) {
        return JSON.parse(cachedResponse);
    }
    var response = postJsonRpc(url, data, headers);
    if (response) {
        cache.put(cacheKey, JSON.stringify(response), cacheTtl);
    }
    return response;
}
/**
 * Take a dictionary and return the URL encoded parameters
 */
function encodeQueryData(parameters) {
    var queryParameters = [];
    for (var key in parameters) {
        queryParameters.push(encodeURIComponent(key) + "=" + encodeURIComponent(parameters[key]));
    }
    return "?" + queryParameters.join("&");
}
