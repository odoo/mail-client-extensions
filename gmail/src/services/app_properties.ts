export function getOdooServerUrl() {
    return PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL");
}
export function setOdooServerUrl(url: string) {
    PropertiesService.getUserProperties().setProperty("ODOO_SERVER_URL", url);
}
