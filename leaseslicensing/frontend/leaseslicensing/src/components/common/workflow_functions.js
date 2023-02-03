import { api_endpoints, helpers } from '@/utils/hooks'
import '../../../../../static/leaseslicensing/css/workflow.css'

/**
 * Sends a referral reminder to the referrer
 * @param {number} _id The referral ID
 * * @param {string} user The referrer's username
 */
export async function remindReferral(_id, user){
    fetch(helpers.add_endpoint_json(api_endpoints.referrals,_id+'/remind')).then(async response => {
        if (!response.ok) {
                return response.json().then(json => { throw new Error(json); });
            } else {
                return response.json();
        }
    }).then(data => {
        swal.fire({
            title: 'Referral Reminder',
            text: 'A reminder has been sent to '+user,
            icon: 'success',
            // Have swal2 popovers placed above bootstrap popovers
            customClass: {
                container: 'swal2-popover'
            }
        })
    }).catch(error => {
        swal.fire({
            title: 'Proposal Error',
            text: error["message"],
            icon: 'error',
            customClass: {
                container: 'swal2-popover'
            }
        })
    });
}

/**
 * Recalls a referral from the referrer
 * @param {number} _id The referral ID
 * * @param {string} user The referrer's username
 */
export async function recallReferral(_id, user){
    let vm = this;
    const _loading = swal.fire({
        icon: "info",
        title: "Loading...",
        showConfirmButton: false,
        allowOutsideClick: false,
        allowEscapeKey:false,
        didOpen: async () => {
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
        if (typeof(vm["table"]) !== 'undefined') {
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
            text: error["message"],
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
        if (typeof(vm["table"]) !== 'undefined') {
            // Reload the Show Referrals popover table if exists
            vm.table.ajax.reload();
        }
        swal.fire({
            title: 'Referral Resent',
            text: 'The referral has been resent to ' + user,
            icon: 'success',
            customClass: {
                container: 'swal2-popover'
            }
        });
    }).catch(error => {
        swal.fire({
            title: 'Proposal Error',
            text: error["message"],
            icon: 'error',
            customClass: {
                container: 'swal2-popover'
            }
        });
    });
}
