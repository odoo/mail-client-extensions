import Address from './Address';
import EnrichmentInfo, { EnrichmentInfoType } from './EnrichmentInfo';

/***
 * id reserved for empty companies.
 */
const ID_COMPANY_EMPTY: number = -1;

export enum EnrichmentStatus {
    enrichmentAvailable = 0, // means that the company has not been enriched before and could maybe be enriched
    enriched = 1, // means that the company has been previously enriched
    enrichmentEmpty = 2, // means that an attempt was made to enrich the company and that no data was found
}

class Company {
    id: number;
    domain: string;
    name: string;
    website: string;
    image: string; // base64
    address: Address;
    phone: string;
    email: string;
    additionalInfo: {}; //Map<string, string>;

    enrichmentStatus: EnrichmentStatus;

    constructor() {
        this.id = ID_COMPANY_EMPTY;
        this.domain = '';
        this.name = '';
        this.website = '';
        this.phone = '';
        this.address = new Address();
        this.image = '';
        this.email = '';
        this.additionalInfo = {};
    }

    static fromJSON(o: Object, enrichmentInfo?: EnrichmentInfo): Company {
        if (!o) return new Company();
        const company = Object.assign(new Company(), o);
        company.address = Address.fromJSON(o['address']);

        if (enrichmentInfo != null) {
            switch (enrichmentInfo.type) {
                case EnrichmentInfoType.NoData:
                    company.enrichmentStatus = EnrichmentStatus.enrichmentEmpty;
                    break;
                case EnrichmentInfoType.CompanyCreated:
                case EnrichmentInfoType.CompanyUpdated:
                    company.enrichmentStatus = EnrichmentStatus.enriched;
                    break;
            }
        } else if (JSON.stringify(company.additionalInfo) != '{}') {
            company.enrichmentStatus = EnrichmentStatus.enriched;
        } else {
            company.enrichmentStatus = EnrichmentStatus.enrichmentAvailable;
        }

        return company;
    }

    static fromRevealJSON(o: Object): Company {
        const company = new Company();
        company.id = ID_COMPANY_EMPTY;
        company.additionalInfo = o;
        return company;
    }

    static getEmptyCompany = (): Company => {
        const company = new Company();
        company.id = ID_COMPANY_EMPTY;
        return company;
    };

    getDomain(): string {
        let domain = this.domain || this.additionalInfo['domain'] || this.website;
        if (domain && !domain.startsWith('http://') && !domain.startsWith('https://')) {
            domain = 'https://' + domain;
        }
        return domain;
    }

    getBareDomain() {
        let domain = this.domain || this.additionalInfo['domain'];
        if (domain) {
            domain = domain.replace(/(^\w+:|^)\/\//, '');
        }
        return domain;
    }

    getPhone(): string {
        if (this.phone) return this.phone;

        if (this.additionalInfo['phone_numbers'] && this.additionalInfo['phone_numbers'].length > 0)
            return this.additionalInfo['phone_numbers'][0];

        return '';
    }

    getName(): string {
        return this.name || this.additionalInfo['name'];
    }

    getDescription(): string {
        return this.additionalInfo['description'];
    }

    getIndustry(): string {
        const industries = [this.additionalInfo['industry_group'], this.additionalInfo['sub_industry']];
        return industries.filter(Boolean).join(', ');
    }

    getEmployees(): number {
        return this.additionalInfo['employees'];
    }

    getYearFounded(): number {
        return this.additionalInfo['founded_year'];
    }

    getKeywords(): string {
        if (this.additionalInfo['tag']) return this.additionalInfo['tag'].join(', ');
        return '';
    }

    getCompanyType(): string {
        return this.additionalInfo['company_type'];
    }

    getLogoURL(): string {
        return this.additionalInfo['logo'];
    }

    /* "annual_revenue" seems to be a number, often at 0.0 without a currency. Let's ignore this field.
        Data sample: "annual_revenue": 0.0,
                     "estimated_annual_revenue": "$50M-$100M",
    */
    getRevenue(): string {
        return this.additionalInfo['estimated_annual_revenue'];
    }

    getLocation(): string {
        return this.address.getLines().join(', ') || this.additionalInfo['location'];
    }

    getTwitter(): string {
        return this.additionalInfo['twitter'];
    }

    getFacebook(): string {
        return this.additionalInfo['facebook'];
    }

    getLinkedin(): string {
        return this.additionalInfo['linkedin'];
    }

    getCrunchbase(): string {
        return this.additionalInfo['crunchbase'];
    }

    getInitials(): string {
        const name = this.getName();
        if (!name) {
            return '';
        }
        const names = this.name.split(' ');
        let initials = names[0].substring(0, 1).toUpperCase();

        // If the company is more than two words, better only include the first letter of the first word.
        if (names.length == 2) {
            initials += names[1].substring(0, 1).toUpperCase();
        }

        return initials;
    }

    /***
     * Returns True if the company exists in the Odoo database, False otherwise
     */
    isAddedToDatabase(): boolean {
        return this.id && this.id > 0;
    }
}

export default Company;
