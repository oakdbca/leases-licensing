
import { createApp, h, reactive, toRefs } from 'vue';
import CustomRow from '@/components/common/custom_row.vue'

/**
 * Returns table row and cell jQuery objects for a clicked data table expander
 * @param {Proxy} vm
 * @param {Object} obj Expander HTML element
 * @returns jQuery objects for table row and first cell, or an empty list if not expandable
 */
function tr_first_td(vm, obj) {
    let td_link = $(obj);
    if (!(td_link.hasClass(vm.td_expand_class_name) || td_link.hasClass(vm.td_collapse_class_name))){
        // This row is not configured as expandable row (at the rowCallback)
        return []
    }
    // Get <tr> element as jQuery object
    let tr = td_link.closest('tr')
    let first_td = tr.children().first()

    return [tr, first_td]
}

/**
 * Collapses an expanded table row
 * @param {Proxy} vm
 * @param {Object} tr Table row
 * @param {Object} first_td First cell in row
 */
function collapse_row(vm, tr, first_td) {
    let nextElem = tr.next()
    // Collapse
    if(nextElem.is('tr') & nextElem.hasClass(vm.expandable_row_class_name)){
        // Sticker details row is already shown.  Remove it.
        nextElem.fadeOut(500, function(){
            nextElem.remove()
        })
    }
    // Change icon class name to vm.td_expand_class_name
    first_td.removeClass(vm.td_collapse_class_name).addClass(vm.td_expand_class_name)
}


export function expandToggle(vm, obj) {
    let [tr, first_td] = tr_first_td(vm, obj);
    if (typeof(tr) === 'undefined' || typeof(first_td) === 'undefined') {
        return;
    }

    if(first_td.hasClass(vm.td_expand_class_name)){
        // Expand

        // If we don't need to retrieve the data from the server, follow the code below
        let contents = '<div><strong>Site:</strong> (site name here)</div><div><strong>Group:</strong> (group name here)</div>'
        let details_elem = $('<tr class="' + vm.expandable_row_class_name +'"><td colspan="' + vm.number_of_columns + '">' + contents + '</td></tr>')
        details_elem.hide()
        details_elem.insertAfter(tr)
        details_elem.fadeIn(1000)

        // Change icon class name to vm.td_collapse_class_name
        first_td.removeClass(vm.td_expand_class_name).addClass(vm.td_collapse_class_name)
    } else {
        collapse_row(vm, tr, first_td);
    }
}

// used by competitive process
export function expandToggleCP(vm, obj) {
    let [tr, first_td] = tr_first_td(vm, obj);
    if (typeof(tr) === 'undefined' || typeof(first_td) === 'undefined') {
        return;
    }

    let $row = vm.$refs.competitive_process_datatable.vmDataTable.row(tr)
    let full_data = $row.data()
    if(first_td.hasClass(vm.td_expand_class_name)){
        // Expand
        // If we don't need to retrieve the data from the server, follow the code below
        let elem_group = '<div>Group: ' + full_data.group + '</div>'
        let elem_site = '<div>Site: ' + full_data.site + '</div>'
        let elem_applicant = ''
        if (full_data.registration_of_interest){
            elem_applicant = '<div>Applicant: ' + full_data.registration_of_interest.relevant_applicant_name + '</div>'
        }
        let contents = elem_group + elem_site + elem_applicant
        let details_elem = $('<tr class="' + vm.expandable_row_class_name +'"><td colspan="' + vm.number_of_columns + '">' + contents + '</td></tr>')
        details_elem.hide()
        details_elem.insertAfter(tr)
        details_elem.fadeIn(1000)

        // Change icon class name to vm.td_collapse_class_name
        first_td.removeClass(vm.td_expand_class_name).addClass(vm.td_collapse_class_name)
    } else {
        collapse_row(vm, tr, first_td);
    }
}

// used by `table_parties.vue`
export function expandToggleParties(vm, obj) {
    let td_link = $(obj)
    if (!(td_link.hasClass(vm.td_expand_class_name) || td_link.hasClass(vm.td_collapse_class_name))){
        // This row is not configured as expandable row (at the rowCallback)
        return
    }
    let tr = td_link.closest('tr')
    let first_td = tr.children().first()

    // Get full data of this row
    let $row = vm.$refs.parties_datatable.vmDataTable.row(tr)
    let full_data = $row.data()

    if(full_data.expanded){
        // Collapse
        let siblings = tr.next('tr.' + vm.expandable_row_class_name)
        siblings.fadeOut(500, function(){
            siblings.remove()
            // Change icon
            first_td.removeClass(vm.td_collapse_class_name).addClass(vm.td_expand_class_name)
            // Hide child row, where hidden columns are
            $row.child.hide()
            // Toggle flag
            full_data.expanded = false


            if (full_data.id in vm.custom_row_apps){
                vm.custom_row_apps[full_data.id].unmount()
                vm.custom_row_apps[full_data.id] = undefined
            }
            // if (full_data.custom_row_app){
            //     // Component mounted once cannot be remount easily.  Therefore unmount and delete it completely here and then when required, create it again.
            //     full_data.custom_row_app.unmount()
            //     full_data.custom_row_app = undefined
            // }
        })
    } else {
        // Expand
        let details_elem = $('<tr class="' + vm.expandable_row_class_name +'"><td id="custom_row_' + full_data.id + '"></td></tr>')
        details_elem.hide()
        details_elem.insertAfter(tr)
        vm.updateCustomRowColSpan()

        // -----------------------
        // Add vue component dynamically
        // -----------------------
        // Configure event listener (Ref: https://stackoverflow.com/questions/67516974/vue3-listen-to-event-from-dynamically-created-child-component-on-replacement)
        const props = {
            party_full_data: full_data,
            competitive_process_id: vm.competitive_process_id,
            accessing_user: vm.accessing_user,
            processing: vm.processing,
            discarded: vm.discarded,
            declined: vm.declined,
        }
        // Make the props reactive
        const react = reactive(props);
        // Keep an instance of this custom row
        let instance;
        let custom_row_app = createApp({
            setup() {
                return {
                    ...toRefs(react),
                }
            },
            created() {
                // Get a reference to this custom row instance
                instance = this;
              },
            // Render the dynamically added custom row and catch
            // events of newly added details and emit them to the
            // `competitive_process` vue files
            render: () => h(CustomRow,
                        {...react,
                            onAddDetail: e => vm.$emit("add-detail", e)
                        })

        })
        custom_row_app.mount('#custom_row_' + full_data.id)
        // -----------------------

        // Store custom_row_app in order to unmount when being hidden
        // full_data.custom_row_app = custom_row_app
        custom_row_app["instance"] = instance;
        vm.custom_row_apps[full_data.id] = custom_row_app

        details_elem.fadeIn(1000)

        // Change icon
        first_td.removeClass(vm.td_expand_class_name).addClass(vm.td_collapse_class_name)
        // Show child row, where hidden columns are
        $row.child.show()
        // Toggle flag
        full_data.expanded = true
    }
}