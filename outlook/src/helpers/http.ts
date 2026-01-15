import api from './api'

export enum HttpVerb {
    GET = 'GET',
    POST = 'POST',
}
export enum ContentType {
    Json = 'application/json',
    Http = 'multipart/form-data',
}
export function sendHttpRequest(
    method: HttpVerb,
    url: string,
    contentType?: ContentType,
    token?: string,
    data?: Object,
    rpc?: boolean
): { promise: Promise<any>; cancel: () => void } {
    let cancel: () => void
    const promise = new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        xhr.open(method, url)

        if (contentType) {
            xhr.setRequestHeader('Content-Type', contentType)
        }

        if (token) {
            xhr.setRequestHeader('Authorization', token)
        }

        xhr.setRequestHeader('Accept-Language', '*')

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(rpc ? JSON.parse(xhr.response).result : xhr.response)
            } else {
                reject(new Error(xhr.status.toString()))
            }
        }
        xhr.onerror = function () {
            console.error(xhr)
            reject(new Error(xhr.status.toString()))
        }

        if (contentType == ContentType.Json) {
            if (rpc) {
                const rpc = {
                    jsonrpc: '2.0',
                    id: 0,
                    method: 'call',
                    params: data || {},
                }
                xhr.send(JSON.stringify(rpc))
            } else {
                xhr.send(JSON.stringify(data || {})) // Empty object at least, otherwise wrong json format error.
            }
        } else if (contentType == ContentType.Http) {
            // Generate the form based on a javascript object
            const formData = new FormData()
            for (const [prop, values] of Object.entries(data)) {
                formData.append(prop, values)
            }
            xhr.send(formData)
        }

        cancel = () => {
            xhr.abort()
            reject()
        }
    })
    return { promise, cancel }
}

export async function postJsonRpc(
    relativeUrl: string,
    params: Record<string, any>
): Promise<any> {
    for (const key in params) {
        // don't send null values
        if (params[key] === undefined || params[key] === null) {
            params[key] = false
        }
    }
    const odooAccessToken = localStorage.getItem('odoo_access_token')
    const baseUrl = localStorage.getItem('odoo_url')
    if (!odooAccessToken?.length || !baseUrl?.length) {
        return null
    }

    const request = sendHttpRequest(
        HttpVerb.POST,
        baseUrl + relativeUrl,
        ContentType.Json,
        odooAccessToken,
        params,
        true
    )
    try {
        return await request.promise
    } catch (error) {
        console.error(error)
        return null
    }
}

/**
 * Make an HTTP request to the Odoo database to verify that the server
 * is reachable and that the mail plugin module is installed.
 *
 * Returns the version of the addin that is supported if it's reachable, null otherwise.
 */
export async function getSupportedAddinVersion(
    baseURL: string
): Promise<number | null> {
    if (!baseURL) {
        return null
    }
    const request = sendHttpRequest(
        HttpVerb.POST,
        baseURL + api.CHECK_VERSION,
        ContentType.Json,
        null,
        {},
        true
    )

    try {
        return await request.promise
    } catch {
        return null
    }
}

/**
 * Open a dialog and ask the permission on the Odoo side.
 *
 * Return null if the user refused the permission and return the authentication
 * code if the user accepted the permission.
 */
export async function openOdooLoginDialog(baseURL: string): Promise<string> {
    const href = window.location.href
    const addInBaseURL = href.substring(0, href.lastIndexOf('/'))
    const options = {
        height: 65,
        width: 30,
        promptBeforeOpen: true,
    }

    const redirectToAddin = encodeURIComponent(
        addInBaseURL + '/login_success.html'
    )
    const redirectToAuthPage = encodeURIComponent(
        api.AUTH_CODE_PAGE +
            '?scope=' +
            api.OUTLOOK_SCOPE +
            '&friendlyname=' +
            api.OUTLOOK_FRIENDLY_NAME +
            '&redirect=' +
            redirectToAddin
    )
    const loginURL =
        baseURL + api.LOGIN_PAGE + '?redirect=' + redirectToAuthPage
    const url = `${addInBaseURL}/login_redirect.html?dialogredir=${loginURL}`

    return new Promise((resolve, _) => {
        Office.context.ui.displayDialogAsync(url, options, (asyncResult) => {
            const dialog = asyncResult.value
            dialog.addEventHandler(
                Office.EventType.DialogMessageReceived,
                (argsStr) => {
                    if ('error' in argsStr) {
                        resolve(null)
                        return
                    }
                    const args = JSON.parse(argsStr.message || '')
                    if (args.success) {
                        const authCode = args.auth_code
                        resolve(authCode?.length ? authCode : null)
                    } else {
                        resolve(null)
                    }
                }
            )
        })
    })
}

/**
 * Make an HTTP request to the Odoo database to exchange the authentication code
 * for a long term access token.
 *
 * Return the access token or null if something went wrong.
 */
export async function exchangeAuthCodeForAccessToken(
    baseURL: string,
    authCode: string
): Promise<string> {
    try {
        const response = await sendHttpRequest(
            HttpVerb.POST,
            baseURL + api.GET_ACCESS_TOKEN,
            ContentType.Json,
            null,
            { auth_code: authCode },
            true
        ).promise
        const accessToken = response.access_token
        return accessToken && accessToken.length ? accessToken : null
    } catch (error) {
        console.error(error)
        return null
    }
}

export function getOdooRecordURL(model: string, recordId: number): string {
    const baseUrl = localStorage.getItem('odoo_url')
    return (
        baseUrl +
        `/mail_plugin/redirect_to_record/${model}/?record_id=${recordId}`
    )
}
