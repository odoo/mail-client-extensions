export enum EnrichmentInfoType {
    None = 'none',
    CompanyCreated = 'company_created',
    NoData = 'no_data',
    InsufficientCredit = 'insufficient_credit',
    Other = 'other',
    NotConnected_NoData = 'missing_data',
    NotConnected_InsufficientCredit = 'exhausted_requests',
    NotConnected_InternalError = 'internal_error'
}
class EnrichmentInfo {
    type: EnrichmentInfoType;
    info: string;

    constructor(type?:EnrichmentInfoType, info?:string) {
        this.type = type || EnrichmentInfoType.None;
        this.info = info || this.getTypicalMessage(this.type);
    }

    public getTypicalMessage(type: EnrichmentInfoType) {
        switch (type) {
            case EnrichmentInfoType.None:
                return "";
            case EnrichmentInfoType.CompanyCreated:
                return "Company created!"
            case EnrichmentInfoType.NoData:
            case EnrichmentInfoType.NotConnected_NoData:
                return "Could not autocomplete the company: no data found";
            case EnrichmentInfoType.InsufficientCredit:
                return "You don't have enough credit to enrich";
            case EnrichmentInfoType.NotConnected_InsufficientCredit:
                return "Oops, looks like you have exhausted your free enrichment requests. Please log in to try again";
            case EnrichmentInfoType.Other:
            case EnrichmentInfoType.NotConnected_InternalError:
                return "Could not autocomplete the company. Internal error. Try again later...";
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