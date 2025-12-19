/**
 * Format the given URL by checking the protocol part and removing trailing "/".
 */
export function formatUrl(url: string): string {
    if (!url || !url.length) {
        return;
    }
    if (url.indexOf("http://") !== 0 && url.indexOf("https://") !== 0) {
        url = "https://" + url;
    }

    // Remove trailing "/"
    return url.replace(/\/+$/, "");
}

export function htmlEscape(content: string): string {
    return content
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
