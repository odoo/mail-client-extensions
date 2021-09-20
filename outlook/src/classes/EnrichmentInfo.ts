import { _t } from '../utils/Translator';

export enum EnrichmentInfoType {
    None = 'none',
    CompanyCreated = 'company_created',
    CompanyUpdated = 'company_updated',
    NoData = 'no_data',
    InsufficientCredit = 'insufficient_credit',
    Other = 'other',
    ConnectionError = 'connection_error',
    EnrichContactWithNoEmail = 'enrich_contact_with_no_email',
    NotConnected_NoData = 'missing_data',
    NotConnected_InsufficientCredit = 'exhausted_requests',
    NotConnected_InternalError = 'internal_error',
    CouldNotGetTranslations = 'could_not_get_translations',
    OdooCustomError = 'odoo_custom_error',
}
class EnrichmentInfo {
    type: EnrichmentInfoType;
    info: string;

    constructor(type?: EnrichmentInfoType, info?: string) {
        this.type = type || EnrichmentInfoType.None;
        this.info = info;
    }

    getTypicalMessage = () => {
        switch (this.type) {
            case EnrichmentInfoType.None:
                return '';
            case EnrichmentInfoType.CompanyCreated:
                return _t('Company created');
            case EnrichmentInfoType.CompanyUpdated:
                return _t('Company updated');
            case EnrichmentInfoType.NoData:
            case EnrichmentInfoType.NotConnected_NoData:
                return _t('No data found for this email address.');
            case EnrichmentInfoType.InsufficientCredit:
                return _t("You don't have enough credit to enrich.");
            case EnrichmentInfoType.NotConnected_InsufficientCredit:
                //no need to translate since it appears only when the user is not logged in
                return 'Oops, looks like you have exhausted your free enrichment requests. Please log in to try again.';
            case EnrichmentInfoType.Other:
                return _t('Something bad happened. Please, try again later.');
            case EnrichmentInfoType.NotConnected_InternalError:
                return _t('Could not autocomplete the company. Internal error. Try again later...');
            case EnrichmentInfoType.ConnectionError:
                return _t('Could not connect to your database. Please try again.');
            case EnrichmentInfoType.EnrichContactWithNoEmail:
                return _t('This contact has no email address, no company could be enriched.');
            case EnrichmentInfoType.CouldNotGetTranslations:
                return _t('An error has occurred when trying to fetch translations.');
            case EnrichmentInfoType.OdooCustomError:
                return this.info;
            default:
                return '';
        }
    };

    static fromJSON(o: Object): EnrichmentInfo {
        return Object.assign(new EnrichmentInfo(), o);
    }
}

export default EnrichmentInfo;
