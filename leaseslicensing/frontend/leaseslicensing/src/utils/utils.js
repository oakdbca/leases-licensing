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
}
