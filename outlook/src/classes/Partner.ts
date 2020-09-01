import Company from './Company';
import EnrichmentInfo from './EnrichmentInfo';

class Partner {
    id: number;
    name: string;
    title: string; // job title
    phone: string;
    mobile: string;
    email: string;
    company: Company;
    image: string;
    initials: string;
    enrichmentInfo: EnrichmentInfo;
    created: boolean;

    constructor() {
        this.id = -1;
        this.name = "";
        this.title = "";
        this.phone = "";
        this.mobile = "";
        this.email = "";
        this.company = new Company();
        this.image = "";
        this.enrichmentInfo = new EnrichmentInfo();
        this.created = false;
    }

    getInitials() : string {
        if (!this.name) {
            return "";
        }
        const names = this.name.split(" ");
        let initials = names[0].substring(0, 1).toUpperCase();
        
        if (names.length > 1) {
            initials += names[names.length - 1].substring(0, 1).toUpperCase();
        }
        return initials;
    };

    static fromJSON(o: Object): Partner {
        if (!o) return new Partner();
        const partner = Object.assign(new Partner(), o);
        partner.company = Company.fromJSON(o['company']);
        partner.enrichmentInfo = EnrichmentInfo.fromJSON(o['enrichment_info']);
        return partner;
    }
}

export default Partner;