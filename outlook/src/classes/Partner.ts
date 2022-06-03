import Company from './Company';
import EnrichmentInfo from './EnrichmentInfo';
import Lead from './Lead';
import HelpdeskTicket from './HelpdeskTicket';
import Task from './Task';

/***
 * id value for partners which have not been yet added to a Odoo database
 */
const ID_PARTNER_NOT_FROM_DATABASE: number = -1;

class Partner {
    id: number;
    name: string;
    title: string; // job title
    phone: string;
    mobile: string;
    email: string;
    company: Company;
    image: string;
    enrichmentInfo: EnrichmentInfo;
    created: boolean;
    leads?: Lead[];
    tasks?: Task[];
    tickets?: HelpdeskTicket[];
    isCompany: boolean;
    canWriteOnPartner: boolean;

    constructor() {
        this.id = ID_PARTNER_NOT_FROM_DATABASE;
        this.name = '';
        this.title = '';
        this.phone = '';
        this.mobile = '';
        this.email = '';
        this.company = new Company();
        this.image = '';
        this.enrichmentInfo = new EnrichmentInfo();
        this.created = false;
        this.isCompany = false;
        this.canWriteOnPartner = true;
    }

    /***
     * Creates a partner which is not stored in a Odoo database
     * @param name
     * @param email
     * @param company
     */
    static createNewPartnerFromEmail = (name: string, email: string): Partner => {
        const partner = new Partner();
        partner.name = name;
        partner.email = email;
        return partner;
    };

    static fromJSON(o: Object): Partner {
        if (!o) return new Partner();
        const partner = Object.assign(new Partner(), o);
        partner.company = Company.fromJSON(o['company']);
        partner.enrichmentInfo = EnrichmentInfo.fromJSON(o['enrichment_info']);
        partner.isCompany = o['is_company'];
        // Undefined is considered as True for retro-compatibility
        partner.canWriteOnPartner = o['can_write_on_partner'] !== false;
        return partner;
    }

    /***
     * Given a list of partners having their name and/or email respectively matching a contact's name and/or email,
     * this method returns a sorted list of the best matched partners, partners are sorted according to these criteria:
     * 1) partners with an email and name which both equals the provided contact email and name
     * 2) partners with an email which is equal to the provided contact email
     * 3) partners with a name which is equal to the provided contact name
     * @param email the contact's email
     * @param name the contact's name
     * @param partners a list of partners
     */
    static sortBestMatches(email: string, name: string, partners: Partner[]): Partner[] {
        return partners.sort((p1, p2) => {
            if (p1.email === email && (p2.email !== email || p1.name == name)) {
                return -1;
            } else {
                return 1;
            }
        });
    }

    /***
     * return a string containing the two initials of a display name, we return the initials of the first and the
     * last "words" composing the displayName, words having a length < 2 and which contain non alphabetical characters are
     * not taken into account.
     */
    getInitials(): string {
        //get all words having a length > 2 and containing only letters
        const rgx = new RegExp(/(\p{L}{1})\p{L}+/, 'gu');

        const initials = [...this.name.matchAll(rgx)] || [];

        return ((initials.shift()?.[1] || '') + (initials.pop()?.[1] || '')).toUpperCase();
    }

    /***
     * Returns True if the partner exists in the Odoo database, False otherwise
     */
    isAddedToDatabase(): boolean {
        return this.id && this.id > 0;
    }
}

export default Partner;
