import { api_endpoints, helpers } from '@/utils/hooks';
import '../../../../../static/leaseslicensing/css/workflow.css';

/**
 * Sends a referral reminder to the referrer
 * @param {number} _id The referral ID
 * * @param {string} user The referrer's username
 */
export async function remindReferral(_id, user) {
    fetch(helpers.add_endpoint_json(api_endpoints.referrals, _id + '/remind')).then(async response => {
        if (!response.ok) {
            return response.json().then(json => { throw new Error(json); });
        } else {
            return response.json();
        }
    }).then(() => {
        // eslint-disable-next-line no-undef
        swal.fire({
            title: 'Referral Reminder',
            text: 'A reminder has been sent to ' + user,
            icon: 'success',
            // Have swal2 popovers placed above bootstrap popovers
            customClass: {
                container: 'swal2-popover'
            }
        });
    }).catch(error => {
        // eslint-disable-next-line no-undef
        swal.fire({
            title: 'Proposal Error',
            text: error['message'],
            icon: 'error',
            customClass: {
                container: 'swal2-popover'
            }
        });
    });
}

/**
 * Recalls a referral from the referrer
 * @param {number} _id The referral ID
 * * @param {string} user The referrer's username
 */
export async function recallReferral(_id, user) {
    let vm = this;
    // eslint-disable-next-line no-undef
    const _loading = swal.fire({
        icon: 'info',
        title: 'Loading...',
        showConfirmButton: false,
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: async () => {
            // eslint-disable-next-line no-undef
            swal.showLoading();
        },
        customClass: {
            container: 'swal2-popover'
        }
    });

    await fetch(helpers.add_endpoint_json(api_endpoints.referrals, _id + '/recall')).then(async response => {
        if (!response.ok) {
            return await response.json().then(json => { throw new Error(json); });
        } else {
            return response.json();
        }
    }).then(async (response) => {
        vm.switchStatus(response.processing_status_id); // 'with_assessor'
        if (typeof (vm['table']) !== 'undefined') {
            // Reload the Show Referrals Popover table if exists
            vm.table.ajax.reload();
        }
        _loading.hideLoading();
        _loading.update({
            showConfirmButton: true,
            title: 'Referral Recall',
            text: 'The referral has been recalled from ' + user,
            icon: 'success'
        });
    }).catch((error) => {
        _loading.hideLoading();
        _loading.update({
            showConfirmButton: true,
            title: 'Proposal Error',
            text: error['message'],
            icon: 'error'
        });
    }).finally(() => {
        // _loading.close();
    });
}

/**
 * Resends a referral reminder to the referrer
 * @param {number} _id The referral ID
 * * @param {string} user The referrer's username
 */
export async function resendReferral(_id, user) {
    let vm = this;
    await fetch(helpers.add_endpoint_json(api_endpoints.referrals, _id + '/resend')).then(async response => {
        if (!response.ok) {
            return await response.json().then(json => { throw new Error(json); });
        } else {
            return response.json();
        }
    }).then(async response => {
        vm.switchStatus(response.processing_status_id); // 'with_referral'
        if (typeof (vm['table']) !== 'undefined') {
            // Reload the Show Referrals popover table if exists
            vm.table.ajax.reload();
        }
        // eslint-disable-next-line no-undef
        swal.fire({
            title: 'Referral Resent',
            text: 'The referral has been resent to ' + user,
            icon: 'success',
            customClass: {
                container: 'swal2-popover'
            }
        });
    }).catch(error => {
        // eslint-disable-next-line no-undef
        swal.fire({
            title: 'Proposal Error',
            text: error['message'],
            icon: 'error',
            customClass: {
                container: 'swal2-popover'
            }
        });
    });
}

/**
 * Updates a list of, e.g. selected items, with `id` .
 * @param {int} id The id of the item to add or remove from the list.
 * @param {Array} list The list to add to.
 * @param {Array} available_items A list of available items of which `id` is a member.
 * @param {Boolean} remove Whether to remove the item from the list. Default false.
 */
export function updateIdListFromAvailable(id, list, available_items, remove) {
    if (!remove) {
        remove = false;
    }

    let found = list.find(element => element.id === parseInt(id));

    if (!found) {
        let item = available_items.find(element => element.id === parseInt(id));
        if (!item) {
            console.warn(`Selected item with id ${id} not found in available items.`);
            return false;
        }
        console.log(`Adding item with id ${id} to list of selected items.`);
        list.push(item);
        return list;
    }

    if (found && remove) {
        console.log(`Removing item with id ${id} from list of selected items.`);
        list = list.filter(element => element.id !== parseInt(id));
        return list;
    }
    return false;
}

/**
 * Discards a proposal.
 * @param {object} proposal A proposal object or a proposal ID
 * @returns an api query Promise
 */
export async function discardProposal(proposal) {
    let proposal_id = proposal.id || proposal;

    return swal.fire({
        title: "Discard Application",
        text: "Are you sure you want to discard this application?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: 'Discard Application',
        confirmButtonColor: '#dc3545'
    }).then(async result => {
        return new Promise((resolve, reject) => {
            if (result.isConfirmed) {
                // Queries the delete endpoint
                fetch(api_endpoints.discard_proposal(proposal_id), { method: 'DELETE', })
                    .then(async response => {
                        const data = await response.json();
                        if (!response.ok) {
                            const error = (data && data.message) || response.statusText;
                            console.log(error)
                            swal.fire({
                                title: 'Error',
                                text: 'The proposal could not be discarded',
                                icon: 'error',
                            });
                            reject(error);
                        }
                        swal.fire({
                            title: 'Discarded',
                            text: 'The application has been discarded',
                            icon: 'success',
                        });
                        resolve(data);
                    });
            } else {
                resolve(proposal);
            }
        }
    )});
}
