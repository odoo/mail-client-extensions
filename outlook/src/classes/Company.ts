import Address from './Address';
class Company {
    id: number;
    domain: string;
    name: string;
    website: string;
    image: string; // base64
    address: Address;
    phone: string;
    email: string;
    additionalInfo: {};//Map<string, string>;

    constructor() {
        this.id = -1;
        this.domain = '';
        this.name = '';
        this.website = '';
        this.phone = '';
        this.address = new Address();
        this.image = '';
        this.email = '';
        this.additionalInfo = {};
    }

    getDomain() : string {
        let domain = this.domain || this.additionalInfo['domain'];
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

    getPhone() : string {
        if (this.phone)
            return this.phone;

        if (this.additionalInfo['phone_numbers'] && this.additionalInfo['phone_numbers'].length > 0)
            return this.additionalInfo['phone_numbers'][0];

        return '';
    }

    getName() : string {
        return this.name || this.additionalInfo['name'];
    }

    getDescription() : string {
        return this.additionalInfo['description'];
    }

    getIndustry() : string {
        // TODO 'sector' ?
        const industries = [this.additionalInfo['industry_group'], this.additionalInfo['sub_industry']]
        return industries.filter(Boolean).join(", ");
    }

    getEmployees() : number {
        // TODO remove the decimal
        return this.additionalInfo['employees'];
    }

    getYearFounded() : number {
        return this.additionalInfo['founded_year'];
    }

    getKeywords() : string {
        if (this.additionalInfo['tag'])
            return this.additionalInfo['tag'].join(', ');
        return '';
    }

    getCompanyType() : string {
        return this.additionalInfo['company_type'];
    }

    getLogoURL() : string {
        return this.additionalInfo['logo'];
    }

    /* "annual_revenue" seems to be a number, often at 0.0 without a currency. Let's ignore this field.
        Data sample: "annual_revenue": 0.0,
                     "estimated_annual_revenue": "$50M-$100M",
    */
    getRevenue() : string {
        return this.additionalInfo['estimated_annual_revenue'];
    }

    // TODO: sort it out with the Address object, note: this location can be directly added to a query to maps:
    // "http://maps.google.com/?q=Koning Albert II-Laan 27, 1000 Brussel, Belgium"
    getLocation() : string {
        return this.additionalInfo['location'];
    }

    getTwitter() : string {
        return this.additionalInfo['twitter'];
    }

    getFacebook() : string {
        return this.additionalInfo['facebook'];
    }

    getLinkedin() : string {
        return this.additionalInfo['linkedin'];
    }

    getCrunchbase() : string {
        return this.additionalInfo['crunchbase'];
    }
    
    getInitials() : string {
        const name = this.getName();
        if (!name) {
            return "";
        }
        const names = this.name.split(" ");
        let initials = names[0].substring(0, 1).toUpperCase();
        
        // If the company is more than two words, better only include the first letter of the first word.
        if (names.length == 2) {
            initials += names[1].substring(0, 1).toUpperCase();
        }

        return initials;
    }

    static fromJSON(o: Object): Company {
        if (!o) return new Company();
        const company = Object.assign(new Company(), o);
        company.address = Address.fromJSON(o['address']);
        return company;
    }

    static fromRevealJSON(o: Object): Company {
        const company = new Company();
        company.additionalInfo = o;
        return company;
    }

}

export default Company;