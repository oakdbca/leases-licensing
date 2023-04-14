import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    fetchCountries: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.countries)
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        reject(error)
                    }
                    resolve(data)
                    console.log('countries: ', data)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                    reject(error)
                })
        });
    },
    fetchRequestUserID: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.request_user_id)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        console.log(error)
                        reject(error);
                    }
                    resolve(data)
                    console.log("account: ", data)
                })
                .catch(error => {
                    console.error("There was an error!", error);
                    reject(error)
                });
        });
    },
    fetchAccount: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.users_api + 'request_user_account/')
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        console.log(error)
                        reject(error);
                    }
                    resolve(data)
                    console.log("account: ", data)
                })
                .catch(error => {
                    console.error("There was an error!", error);
                    reject(error)
                });
        });
    },
    fetchLedgerAccount: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.account_details)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        console.log(error)
                        reject(error);
                    }
                    resolve(data)
                    console.log("account: ", data)
                })
                .catch(error => {
                    console.error("There was an error!", error);
                    reject(error)
                });
        });
    },
    fetchOrganisation: function (id) {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.organisations + id + '/')
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        reject(error)
                    }
                    console.log('organisation: ', data)
                    resolve(data)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                    reject(error)
                })
        });
    },
    fetchOrganisationRequests: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.organisation_requests)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        console.log(error)
                        reject(error);
                    }
                    resolve(data)
                    console.log("organisation requests: ", data)
                })
                .catch(error => {
                    console.error("There was an error!", error);
                    reject(error)
                });
        });
    },
    fetchOrganisationPermissions: function (id) {
        return new Promise((resolve, reject) => {
            fetch(helpers.add_endpoint_join(api_endpoints.my_organisations, id))
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        console.log(error)
                        reject(error);
                    }
                    resolve(data)
                    console.log("organisation permissions: ", data)
                })
                .catch(error => {
                    console.error("There was an error!", error);
                    reject(error)
                });
        });
    },
}
