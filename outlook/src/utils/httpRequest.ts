export enum HttpVerb {
    GET = "GET",
    POST = "POST"
}
export enum ContentType {
    Json = "application/json",
    Http = "multipart/form-data"
}
export const sendHttpRequest = function(method: HttpVerb, url: string, contentType?: ContentType, token?: string, data?: Object, rpc?: boolean) : {promise: Promise<any>,  cancel: () => void} {
    let cancel: () => void;
    const promise = new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open(method, url);
        
        if (contentType) {
            xhr.setRequestHeader("Content-Type", contentType);
        }
        
        if (token) {
            xhr.setRequestHeader("Authorization", token);
        }

        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(xhr.response);
            } else {
                reject(new Error(xhr.status.toString()));
            }
        }
        xhr.onerror = function() {
            console.log(xhr);
            reject(new Error(xhr.status.toString()));
        }
        
        if (contentType == ContentType.Json) {
            if (rpc) {
                const rpc = {
                    jsonrpc: '2.0',
                    id: null,
                    method: 'call',
                    params: data || {}
                }
                xhr.send(JSON.stringify(rpc));
            } else {
                xhr.send(JSON.stringify(data || {})); // Empty object at least, otherwise wrong json format error.
            }
        } else if (contentType == ContentType.Http) {
            // Generate the form based on a javascript object
            const formData = new FormData();
            for (const prop in data) {
                formData.append(prop, data[prop])
            }
            xhr.send(formData);
        }

        cancel = () => {
            xhr.abort();
            reject();
        }

    });
    return {promise, cancel};
}