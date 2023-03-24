import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    fetchProposal: function (id) {
        return new Promise((resolve, reject) => {
            this.$http.get(helpers.add_endpoint_json(api_endpoints.proposals, id)).then((response) => {
                resolve(response.body);
            },
                (error) => {
                    reject(error);
                });
        });
    },
    fetchOrganisations: function (id) {
        return new Promise((resolve, reject) => {
            this.$http.get(api_endpoints.organisations).then((response) => {
                resolve(response.body);
            },
                (error) => {
                    reject(error);
                });
        });
    },
    fetchCountries: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.countries)
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    resolve(data)
                    console.log('countries: ', data)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
        });
    },
    fetchOrganisation: function (id) {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.organisations_viewset + id + '/')
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    console.log('organisation: ', data)
                    resolve(data)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
        });
    },
    fetchUser: function (id) {
        return new Promise((resolve, reject) => {
            this.$http.get(helpers.add_endpoint_json(api_endpoints.users, id)).then((response) => {
                resolve(response.body);
            },
                (error) => {
                    reject(error);
                });
        });
    },
    fetchOrgRequestPending: function (id) {
        return new Promise((resolve, reject) => {
            this.$http.get(helpers.add_endpoint_json(api_endpoints.users, id + '/pending_org_requests')).then((response) => {
                resolve(response.body);
            },
                (error) => {
                    reject(error);
                });
        });
    },
    fetchProfile: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.profile)
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    resolve(data)
                    console.log('profile: ', data)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
        });
    },
}
