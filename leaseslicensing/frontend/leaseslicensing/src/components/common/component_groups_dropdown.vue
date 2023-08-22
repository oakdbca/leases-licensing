<template>
    <div class="row col-sm-12">
        <div class="col-sm-9">
            <select
                ref="select_approvalgroupnames"
                v-model="selectedGroupsIds"
                class="form-control"
                :disabled="readonly"
            >
                <option></option>
                <option
                    v-for="group in groups"
                    :key="group.name"
                    :value="group.id"
                >
                    {{ group.name }}
                </option>
            </select>
        </div>
    </div>
</template>

<script>
import { updateIdListFromAvailable } from '@/components/common/workflow_functions.js';
import { utils } from '@/utils/hooks';

export default {
    name: 'ComponentGroupsDropdown',
    props: {
        readonly: {
            type: Boolean,
            default: false,
        },
        proposal: {
            type: Object,
            required: true,
        },
        approval: {
            type: Object,
            required: true,
        },
    },
    data: function () {
        return {
            groups: [],
            selectedGroups: [],
        };
    },
    computed: {
        selectedGroupsIds: function () {
            // Return the ids of selected groups from the group name-dropdown
            return this.selectedGroups.map(({ id }) => id);
        },
    },
    created: async function () {
        let vm = this;

        let initialisers = [utils.fetchGroupsKeyValueList()];

        Promise.all(initialisers).then((data) => {
            vm.groups = data[0];

            // Groups
            // TODO: Currently, groups selected by the applicant are stored in the proposal's
            // groups field. Groups proposed by the assessor are stored in the proposal's
            // `proposed_issuance_approval` dictionary field.
            // Eventually, this should be standardised into just the `groups` field.
            let groups_source = vm.approval.groups
                ? vm.approval.groups
                : vm.proposal.groups
                ? vm.proposal.groups.map(({ id }) => id)
                : [];
            for (let group of vm.groups) {
                if (group && groups_source.includes(group.id)) {
                    vm.selectedGroups.push(group);
                }
            }
        });
    },
    mounted: function () {
        this.$nextTick(() => {
            this.initSelectGroup();
        });
    },
    methods: {
        /**
         * Initialise the select2 control for selecting a group/groups for the application
         */
        initSelectGroup: function () {
            let vm = this;

            $(vm.$refs.select_approvalgroupnames)
                .select2({
                    theme: 'bootstrap-5',
                    allowClear: true,
                    placeholder: 'Select a group',
                    multiple: true,
                })
                .on('select2:select', function (e) {
                    var selected = $(e.currentTarget);
                    vm.updateSelectedGroupsType(selected.val());
                })
                .on('select2:unselecting', function () {
                    var self = $(this);
                    setTimeout(() => {
                        self.select2('close');
                    }, 0);
                })
                .on('select2:unselect', function (e) {
                    let unselected_id = e.params.data.id;
                    vm.updateSelectedGroupsType(unselected_id, true);
                });
        },
        /**
         * Update selected items from multi-select group name-dropdown.
         * @param {int} ids The group id
         * @param {Boolean} remove Whether to remove that group from the list of selected groups.
         */
        updateSelectedGroupsType(ids, remove) {
            let list = this.selectedGroups;
            for (let id of ids) {
                if (!Number(id)) {
                    continue;
                }
                let list_updated = updateIdListFromAvailable(
                    Number(id),
                    list,
                    this.groups,
                    remove
                );
                list = list_updated ? list_updated : list;
            }

            if (list) {
                this.selectedGroups = list;
            } else {
                return false;
            }
        },
    },
};
</script>
