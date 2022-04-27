import Company from './Company';
import Address from './Address';

/*  TODO: Write a version with a doubly linked list tha avoid loading the whole
    cache to prune. And compare the perfs */

class CacheObject {
    version: number;
    timestamp: number;
    company: Company;
    constructor(version: number, timestamp: number, company: Company) {
        this.version = version;
        this.timestamp = timestamp;
        this.company = company;
    }
}

class CompanyCache {
    size: number;
    occupancy: number;
    pruningRatio: number;
    version: number;

    constructor(version: number, size: number, pruningRatio: number) {
        this.size = size;
        this.pruningRatio = pruningRatio;
        this.version = version;

        // Compute the actual occupancy of the current local storage.
        this.occupancy = 0;
        for (const key in localStorage) {
            if (this._isCompanyDomain(key)) {
                const cacheObject: CacheObject = JSON.parse(localStorage.getItem(key));
                // Remove old cache objects. Objects whose version differ from this cache's version.
                if (!('version' in cacheObject) || cacheObject.version != this.version) {
                    localStorage.removeItem(key);
                } else {
                    ++this.occupancy;
                }
            }
        }

        // If this new LRU has different parameters than the previous one, it
        // may already be necessary to prune.
        if (this.occupancy > this.size) {
            this._prune();
        }
    }

    _isCompanyDomain(s: string): boolean {
        return s.startsWith('@');
    }

    _getCacheKeyForCompany(company: Company): string {
        const assignedCompany = Object.assign(new Company(), company); // to get the methods on the basic object.
        return '@' + assignedCompany.getBareDomain();
    }

    _getCacheKeyForDomain(domain: string): string {
        return '@' + domain;
    }

    _getCacheKeyForEmail(email: string): string {
        return '@' + email.split('@')[1];
    }

    /* Pruning 1000 elements with a ratio of 0.5 took 7ms.
           on Chrome 81.0.4044.122, with a Ryzen 3700X 
           Removing only one, the oldest, took 5ms. */
    _prune() {
        // Retrieve all cacheObjects and put them in an array.
        const cacheObjects: CacheObject[] = [];
        for (const key in localStorage) {
            if (this._isCompanyDomain(key)) {
                cacheObjects.push(JSON.parse(localStorage.getItem(key)));
            }
        }

        // Sort them from most recent to oldest.
        cacheObjects.sort((a: CacheObject, b: CacheObject) => {
            if (a.timestamp > b.timestamp) {
                return -1;
            }
            if (a.timestamp < b.timestamp) {
                return 1;
            }
            return 0;
        });

        // How many to keep. A pruning ratio of 0 make the LRU behave like an
        // actual LRU, removing only the one oldest element.
        const toKeep: number = this.pruningRatio
            ? Math.ceil(cacheObjects.length * (1 - this.pruningRatio))
            : cacheObjects.length - 1;

        // Prune.
        for (let i: number = toKeep; i < cacheObjects.length; ++i) {
            localStorage.removeItem(this._getCacheKeyForCompany(cacheObjects[i].company));
        }

        this.occupancy = toKeep;
    }

    add(company: Company) {
        const cacheKey: string = this._getCacheKeyForCompany(company);
        const cacheObject = new CacheObject(this.version, new Date().getTime(), company);

        // Check whether it's just a replace.
        if (localStorage.getItem(cacheKey)) {
            localStorage.setItem(cacheKey, JSON.stringify(cacheObject));
            return;
        }

        // It's an actual add. This will impact the occupancy.
        if (this.occupancy < this.size) {
            localStorage.setItem(cacheKey, JSON.stringify(cacheObject));
            ++this.occupancy;
            return;
        }

        // Pruning time.
        this._prune();

        // Add the new item.
        localStorage.setItem(cacheKey, JSON.stringify(cacheObject));
        ++this.occupancy;
    }

    get(email: string): Company {
        const cacheKey: string = this._getCacheKeyForEmail(email);
        // Get the corresponding CacheObject.
        const cacheObjectstring: string = localStorage.getItem(cacheKey);
        if (cacheObjectstring === null) {
            return null;
        }
        const cacheObject: CacheObject = JSON.parse(cacheObjectstring);

        // Update the timestamp in the LRU.
        cacheObject.timestamp = new Date().getTime();
        localStorage.setItem(cacheKey, JSON.stringify(cacheObject));

        // Return the company.
        // Prototype is assigned to get back class methods. TODO: find a more generic solution.
        Object.setPrototypeOf(cacheObject.company, Company.prototype);
        Object.setPrototypeOf(cacheObject.company.address, Address.prototype);
        return cacheObject.company;
    }

    remove(email: string): boolean {
        const cacheKey: string = this._getCacheKeyForEmail(email);
        // Get the corresponding CacheObject.
        const cacheObjectstring: string = localStorage.getItem(cacheKey);
        if (cacheObjectstring === null) {
            return false;
        }

        // Actually remove the CacheObject.
        localStorage.removeItem(cacheKey);
        --this.occupancy;

        return true;
    }
}

export default CompanyCache;
