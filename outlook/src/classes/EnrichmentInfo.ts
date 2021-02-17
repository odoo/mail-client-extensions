export enum EnrichmentInfoType {
    None = 'none',
    CompanyCreated = 'company_created',
    NoData = 'no_data',
    InsufficientCredit = 'insufficient_credit',
    Other = 'other',
    ConnectionError = 'connection_error',
    EnrichContactWithNoEmail='enrich_contact_with_no_email',
    NotConnected_NoData = 'missing_data',
    NotConnected_InsufficientCredit = 'exhausted_requests',
    NotConnected_InternalError = 'internal_error'
}
class EnrichmentInfo {
    type: EnrichmentInfoType;
    info: string;

    constructor(type?:EnrichmentInfoType, info?:string) {
        this.type = type || EnrichmentInfoType.None;
        this.info = info;
    }

    getTypicalMessage = () => {

        switch (this.type)
        {
            case EnrichmentInfoType.None:
                return "";
            case EnrichmentInfoType.CompanyCreated:
                return "Company created!"
            case EnrichmentInfoType.NoData:
            case EnrichmentInfoType.NotConnected_NoData:
                return "No data found for this email address.";
            case EnrichmentInfoType.InsufficientCredit:
                return "You don't have enough credit to enrich.";
            case EnrichmentInfoType.NotConnected_InsufficientCredit:
                return "Oops, looks like you have exhausted your free enrichment requests. Please log in to try again.";
            case EnrichmentInfoType.Other:
                return "Something bad happened. Please, try again later."
            case EnrichmentInfoType.NotConnected_InternalError:
                return "Could not autocomplete the company. Internal error. Try again later...";
            case EnrichmentInfoType.ConnectionError:
                return "There was a problem contacting the service, please try again later."
            case EnrichmentInfoType.EnrichContactWithNoEmail:
                return "This contact has no email address, no company could be enriched."
            default:
                return "";
        }

    }

    static fromJSON(o: Object): EnrichmentInfo {
        var e = Object.assign(new EnrichmentInfo(), o);
        return e;
    }
}

export default EnrichmentInfo;