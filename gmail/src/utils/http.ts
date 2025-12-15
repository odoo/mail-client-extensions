/**
 * Make a JSON RPC call with the following parameters.
 */
export async function postJsonRpc(url: string, data = {}, headers = {}) {
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

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                ...headers,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const dictResponse = await response.json();
        if (!dictResponse.result) {
            return;
        }

        return dictResponse.result;
    } catch (e) {
        console.error(`HTTP Error: ${e}`);
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
