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
