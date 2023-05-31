<template>
    <!--
        TODO tasks (and ideas):
        - populate tenure, locality, and categorisation from geoserver response (see: map_functions::validateFeature for response values and owsQuery prop for query paramerters)
        - prevent polygon delete after save (or save + status change)
        - polygon redo button
        - polygon edit button (move and add/remove vertices)
        - pass in map tab filterable proposals as prop (see: prop featureCollection)
        - standardise feature tooltip fields (lodgement_date formatting, application_type, processing_status, etc.) across models
        - hide feature tooltip on save as it might overlap the save response modal
        - solve click-select and hover-select for overlapping polygons (cannot click-select a feature for delete if it is under another feature)
        - prevent referrals from creating/editing polygons in the frontend (does not save in backend anyway)
        - disable draw tool for external when model is not in draft status
        - disable draw tool for referral when model is not in with referral status
        - display polygons of approved application on new license application (external 017, internal 041)
        - display polygons from the competitive process of an application that proceeded to a competitive process on the application page
        - implement map on approval details page and map tab
        - keyboard input (del to delete a feature, ctrl+z to undo, ctrl+y to redo, d to draw, etc.)
        - mouse-over control tooltips (zoom-in, -out, toggle-fullscreen have tooltips by default, custom controls should as well)
        - delete old map files
        - rename this file
     -->
    <div>
        <CollapsibleFilters v-if="filterable" :component_title="'Filters' + filterInformation" ref="collapsible_filters"
            @created="collapsible_component_mounted" class="mb-2">
            <div class="row">
                <div class="col-md-3">
                    <label for="">Type {{ filterApplicationsMapApplicationType }}</label>
                    <select class="form-control" v-model="filterApplicationsMapApplicationType">
                        <option value="all" selected>All</option>
                        <option v-for="application_type in application_types" :value="application_type.id"
                            :key="application_type.id">{{ application_type.name_display }}
                        </option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label for="">Status</label>
                    <select class="form-control" v-model="filterApplicationsMapProcessingStatus">
                        <option value="all" selected>All</option>
                        <option v-for="processing_status in processing_statuses" :value="processing_status.id"
                            :key="processing_status.id">{{ processing_status.text }}
                        </option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label for="">Lodged From</label>
                    <div class="input-group date" ref="proposalDateFromPicker">
                        <input type="date" class="form-control" v-model="filterApplicationsMapLodgedFrom">
                    </div>
                </div>
                <div class="col-md-3">
                    <label for="">Lodged To</label>
                    <div class="input-group date" ref="proposalDateToPicker">
                        <input type="date" class="form-control" v-model="filterApplicationsMapLodgedTo">
                    </div>
                </div>
            </div>
        </CollapsibleFilters>

        <div class="d-flex justify-content-end align-items-center mb-2">
            <div @click="displayAllFeatures" class="btn mr-2">Zoom to All</div>
            <button type="button" class="btn btn-primary" @click="geoJsonButtonClicked"><i class="fa-solid fa-download"></i>
                Get GeoJSON</button>
        </div>

        <VueAlert :show.sync="_errorMessage != null" type="danger" style="color: red"><strong> {{ _errorMessage }} </strong></VueAlert>

        <div :id="map_container_id" style="position: relative;">
            <div :id="elem_id" class="map">
                <div class="basemap-button">
                    <img id="basemap_sat" src="../../assets/satellite_icon.jpg" @click="setBaseLayer('sat')" />
                    <img id="basemap_osm" src="../../assets/map_icon.png" @click="setBaseLayer('osm')" />
                </div>
                <div class="optional-layers-wrapper">
                    <!-- Toggle measure tool between active and not active -->
                    <div class="optional-layers-button-wrapper">
                        <div :class="[
                                mode == 'measure' ? 'optional-layers-button-active' : 'optional-layers-button'
                            ]" @click="set_mode.bind(this)('measure')">
                            <img class="svg-icon" src="../../assets/ruler.svg" />
                        </div>
                    </div>
                    <div v-if="drawable" class="optional-layers-button-wrapper">
                        <div :class="[
                                mode == 'draw' ? 'optional-layers-button-active' : 'optional-layers-button'
                            ]" @click="set_mode.bind(this)('draw')">
                            <img class="svg-icon" src="../../assets/pen-icon.svg" />
                        </div>
                    </div>
                    <div style="position:relative">
                        <transition v-if="optionalLayers.length">
                            <div class="optional-layers-button-wrapper">
                                <div class="optional-layers-button" @mouseover="hover = true">
                                    <img src="../../assets/layers.svg" />
                                </div>
                            </div>
                        </transition>
                        <transition v-if="optionalLayers.length">
                            <div div class="layer_options layer_menu" v-show="hover" @mouseleave="hover = false">
                                <template v-for="layer in optionalLayers">
                                    <div class="row">
                                        <input type="checkbox" :id="layer.ol_uid" :checked="layer.values_.visible"
                                            @change="changeLayerVisibility(layer)" class="layer_option col-md-1" />
                                        <label :for="layer.ol_uid" class="layer_option col-md-6">{{ layer.get('title')
                                        }}</label>
                                        <RangeSlider class="col-md-5" @valueChanged='valueChanged($event, layer)' />
                                    </div>
                                </template>
                            </div>
                        </transition>
                    </div>
                    <div v-if="selectedFeatureIds.length>0" class="optional-layers-button-wrapper">
                        <div class="optional-layers-button">
                            <i id="delete_feature" class="svg-icon bi bi-trash3 ll-trash"
                                @click="removeModelFeatures()" />
                            <span class='badge badge-warning' id='selectedFeatureCount'>{{ selectedFeatureIds.length }}</span>
                        </div>
                    </div>
                    <div v-if="showUndoButton" class="optional-layers-button-wrapper">
                        <div class="optional-layers-button" @click="undoLeaseLicensePoint()">
                            <img class="svg-icon" src="../../assets/undo.svg" />
                        </div>
                    </div>
                    <div v-if="showRedoButton" class="optional-layers-button-wrapper">
                        <div class="optional-layers-button" @click="redoLeaseLicensePoint()">
                            <img class="svg-icon" src="../../assets/redo.svg" />
                        </div>
                    </div>
                </div>

                <div id="featureToast" class="toast" style="z-index:9999">
                    <template v-if="selectedModel">
                        <div class="toast-header">
                            <img src="" class="rounded me-2" alt="">
                            <!-- FIXME: Can this be standardised into the same field name? -->
                            <strong class="me-auto">{{ selectedModel.label || selectedModel.application_type_name_display || selectedModel.application_type.name_display }}: {{ selectedModel.lodgement_number }}</strong>
                        </div>
                        <div class="toast-body">
                            <table class="table table-sm">
                                <tbody>
                                    <tr>
                                        <th scope="row">Processing Status</th>
                                        <!-- FIXME: Can this be standardised into the same field name? -->
                                        <td>{{ selectedModel.status || selectedModel.processing_status_display || selectedModel.processing_status }}</td>
                                    </tr>
                                    <!-- TODO: `created_at` is not formatted to DD/MM/YYYY -->
                                    <tr v-if="selectedModel.lodgement_date_display || selectedModel.lodgement_date || selectedModel.created_at">
                                        <th scope="row">Lodgement Date</th>
                                        <!-- FIXME: Can this be standardised into the same field name? -->
                                        <td>{{ selectedModel.lodgement_date_display || selectedModel.lodgement_date || selectedModel.created_at
                                        }}</td>
                                    </tr>
                                    <tr v-if="selectedModel.polygon_source">
                                        <th scope="row">Polygon Source</th>
                                        <td>{{ selectedModel.polygon_source
                                        }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </template>
                </div>

            </div>
            <div id="coords"></div>
            <BootstrapSpinner v-if="!proposals" class="text-primary" />
            <BootstrapSpinner v-if="redirectingToModelDetails || queryingGeoserver" class="text-primary" />

        </div>
        <div class="row">
            <div class="col-sm-6"></div>
            <div class="col-sm-6">
                <div id="legend_title"></div>
                <div id="legend">
                    <img src="" />
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid';
import { api_endpoints, helpers, constants, utils } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'
import VueAlert from '@vue-utils/alert.vue'

import { toRaw } from 'vue';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import TileWMS from 'ol/source/TileWMS';
import { Draw, Select } from 'ol/interaction';
import Feature from 'ol/Feature'
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import { FullScreen as FullScreenControl } from 'ol/control';
import { LineString, Point, Polygon } from 'ol/geom';
import { fromLonLat, toLonLat, transform, Projection } from 'ol/proj';
import GeoJSON from 'ol/format/GeoJSON';
import MeasureStyles, { formatLength } from '@/components/common/measure.js'
import RangeSlider from '@/components/forms/range_slider.vue'
import { addOptionalLayers, set_mode, baselayer_name, polygon_style } from '@/components/common/map_functions.js'

export default {
    name: 'MapComponentWithFiltersV2',
    emits: [
            'filter-appied',
            'validate-feature',
            ],
    props: {
        level: {
            type: String,
            required: true,
            validator: function (val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true : false;
            }
        },
        filterApplicationsMapApplicationType_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationType',
        },
        filterApplicationsMapProcessingStatus_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationStatus',
        },
        filterApplicationsMapLodgedFrom_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationLodgedFrom',
        },
        filterApplicationsMapLodgedTo_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationLodgedTo',
        },
        /**
         * The context of the map. This is used to determine which layers to show on the map.
         * The context should be a model object, e.g. a Proposal, Application, etc.
         * Used to allocate ids, labels, etc to new features
        */
        context: {
            type: Object,
            required: false,
            default: null,
        },
        /**
         * Ids of porposals to be fetched by the map componment and displayed on the map.
         * Negative values fetch no proposals
         * Positive values fetch proposals with those ids
         * Empty list `[]` fetches all proposals
         */
        proposalIds: {
            type: Array,
            required: false,
            default: [],
        },
        /**
         * A geojson feature collection of features (possibvly related to the context) to display on the map.
         */
        featureCollection: {
            type: Object,
            required: false,
            default: {"features": [], "type": "FeatureCollection"},
            validator: function (val) {
                return val.type == 'FeatureCollection' ? true : false;
            }
        },
        /**
         * A classifier to style the features by.
         * `model` displays all features belonging to the same model by the same (randomly generated) color
         * `assessor` displays all features by same color depending on the role of the user who created the feature
         * @values model, assessor
         */
        styleBy: {
            type: String,
            required: false,
            default: 'model',
            validator: function (val) {
                let options = ['model', 'assessor'];
                return options.indexOf(val) != -1 ? true : false;
            }
        },
        /**
         * Color definitions for the features to be used when styling by `assessor`
         * @values unknown, draw, applicant, assessor
         */
        featureColors: {
            type: Object,
            required: false,
            default: () => {
                return {
                    "unknown": "#9999", // greyish
                    "draw": "#00FFFF", // cyan
                    "applicant": "#00FF0077",
                    "assessor": "#0000FF77",
                }
            },
            validator: function (val) {
                let options = ['unknown', 'draw', 'applicant', 'assessor'];
                Object.keys(val).forEach(key => {
                    if (!options.includes(key.toLowerCase())) {
                        console.error('Invalid feature color key: ' + key);
                        return false;
                    }
                    // Invalid color values will evaluate to an empty string
                    let test = new Option().style
                    test.color = val[key];
                    if (test.color === '') {
                        console.error(`Invalid ${key} color value: ${val[key]}`);
                        return false;
                    }
                });
                return true;
            }
        },
        /**
         * A dictionary of query parameters to pass to the WFS geoserver
         * The parent component needs to add the `cql_filter` parameter to filter the features by a spatial opration
         */
        owsQuery: {
            type: Object,
            required: false,
            default: () => {
                return {
                    "version": "1.0.0", // WFS version
                    "landwater": {
                        "typeName": "public:dbca_legislated_lands_and_waters",
                        "srsName": "EPSG:4326",
                        "propertyName": "wkb_geometry", // Default to query for feature geometries only
                        "geometry": "wkb_geometry", // Geometry name (not `the_geom`)
                    },
                }
            }
        },
        /**
         * Whether to display a filter component above the map
         */
        filterable: {
            type: Boolean,
            required: false,
            default: true,
        },
        /**
         * Whether to enable drawing of new features
         */
        drawable: {
            type: Boolean,
            required: false,
            default: false,
        },
        /**
         * Whether to enable selecting existing features (e.g. for deletion)
         */
        selectable: {
            type: Boolean,
            required: false,
            default: false,
        },
    },
    data() {
        let vm = this;
        return {
            // selected values for filtering
            filterApplicationsMapApplicationType: sessionStorage.getItem(vm.filterApplicationsMapApplicationType_cache_name) ? sessionStorage.getItem(vm.filterApplicationsMapApplicationType_cache_name) : 'all',
            filterApplicationsMapProcessingStatus: sessionStorage.getItem(vm.filterApplicationsMapProcessingStatus_cache_name) ? sessionStorage.getItem(vm.filterApplicationsMapProcessingStatus_cache_name) : 'all',
            filterApplicationsMapLodgedFrom: sessionStorage.getItem(vm.filterApplicationsMapLodgedFrom_cache_name) ? sessionStorage.getItem(vm.filterApplicationsMapLodgedFrom_cache_name) : '',
            filterApplicationsMapLodgedTo: sessionStorage.getItem(vm.filterApplicationsMapLodgedTo_cache_name) ? sessionStorage.getItem(vm.filterApplicationsMapLodgedTo_cache_name) : '',

            // filtering options
            application_types: null,
            processing_statuses: null,
            select2AppliedToApplicationType: false,
            select2AppliedToApplicationStatus: false,

            elem_id: uuid(),
            map_container_id: uuid(),
            map: null,
            tileLayerMapbox: null,
            tileLayerSat: null,
            optionalLayers: [],
            hover: false,
            mode: 'normal',
            drawForMeasure: null,
            drawForModel: null,
            newFeatureId: 0,
            measurementLayer: null,
            style: MeasureStyles.defaultStyle,
            segmentStyle: MeasureStyles.segmentStyle,
            labelStyle: MeasureStyles.labelStyle,
            segmentStyles: null,
            content_element: null,
            featureToast: null,
            selectedFeature: null,
            selectedModel: null,
            redirectingToModelDetails: false,
            queryingGeoserver: false,
            proposals: [],
            filteredProposals: [],
            modelQuerySource: null,
            modelQueryLayer: null,
            selectedFeatureIds: [],
            lastPoint: null,
            sketchCoordinates: [[]],
            sketchCoordinatesHistory: [[]],
            defaultColor: '#eeeeee',
            clickSelectStroke: new Stroke({
                    color: 'rgba(255, 0, 0, 0.7)',
                    width: 2,
                }),
            hoverFill: new Fill({
                    color: 'rgba(255, 255, 255, 0.5)',
                }),
            hoverStroke: new Stroke({
                    color: 'rgba(255, 255, 255, 0.5)',
                    width: 1,
                }),
            set_mode: set_mode,
            _errorMessage: null,
        }
    },
    computed: {
        filterApplied: function () {
            let filter_applied = true
            if (
                this.filterApplicationsMapProcessingStatus === 'all' && this.filterApplicationsMapApplicationType === 'all' &&
                this.filterApplicationsMapLodgedFrom.toLowerCase() === '' &&
                this.filterApplicationsMapLodgedTo.toLowerCase() === ''
            ) {
                filter_applied = false
            }
            return filter_applied
        },
        filterApplicationsMapLodgedFromMoment: function () {
            return this.filterApplicationsMapLodgedFrom ? moment(this.filterApplicationsMapLodgedFrom) : null
        },
        filterApplicationsMapLodgedToMoment: function () {
            return this.filterApplicationsMapLodgedTo ? moment(this.filterApplicationsMapLodgedTo) : null
        },
        filterInformation: function () {
            if (this.proposals.length === this.filteredProposals.length) {
                return ' (Showing all Applications)'
            } else {
                return ` (Showing ${this.filteredProposals.length} of ${this.proposals.length} Applications)`
            }
        },
        showUndoButton: function () {
            return this.mode == 'draw' &&
                this.drawForModel &&
                this.drawForModel.getActive() &&
                this.sketchCoordinates.length > 1
        },
        showRedoButton: function () {
            return false;
            // Todo: The redo button is partially implemented so it is disabled for now.
            return this.mode == 'draw' &&
                this.drawForModel &&
                this.drawForModel.getActive() &&
                this.sketchCoordinatesHistory.length > this.sketchCoordinates.length
        },
    },
    components: {
        CollapsibleFilters,
        RangeSlider,
        VueAlert,
        helpers,
    },
    watch: {
        filterApplicationsMapApplicationType: function () {
            console.log('filterApplicationsMapApplicationType', this.filterApplicationsMapApplicationType)
            this.applyFiltersFrontEnd();
            sessionStorage.setItem(this.filterApplicationsMapApplicationType_cache_name, this.filterApplicationsMapApplicationType);
            this.$emit('filter-appied');
        },
        filterApplicationsMapProcessingStatus: function () {
            this.applyFiltersFrontEnd();
            sessionStorage.setItem(this.filterApplicationsMapProcessingStatus_cache_name, this.filterApplicationsMapProcessingStatus);
            this.$emit('filter-appied');
        },
        filterApplicationsMapLodgedFrom: function () {
            this.applyFiltersFrontEnd();
            sessionStorage.setItem('filterApplicationsMapLodgedFromForMap', this.filterApplicationsMapLodgedFrom);
            this.$emit('filter-appied');
        },
        filterApplicationsMapLodgedTo: function () {
            this.applyFiltersFrontEnd();
            sessionStorage.setItem('filterApplicationsMapLodgedToForMap', this.filterApplicationsMapLodgedTo);
            this.$emit('filter-appied');
        },
        filterApplied: function () {
            if (this.$refs.collapsible_filters) {
                // Collapsible component exists
                this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
            }
        },

    },
    methods: {
        updateFilters: function () {
            this.$nextTick(function () {
                console.log('updateFilters')
                this.filterApplicationsMapApplicationType = sessionStorage.getItem(this.filterApplicationsMapApplicationType_cache_name) ? sessionStorage.getItem(this.filterApplicationsMapApplicationType_cache_name) : 'all';
                console.log('this.filterApplicationsMapApplicationType', this.filterApplicationsMapApplicationType)
                console.log('sessionStorage.getItem(this.filterApplicationsMapProcessingStatus_cache_name)', sessionStorage.getItem(this.filterApplicationsMapProcessingStatus_cache_name))
                this.filterApplicationsMapProcessingStatus = sessionStorage.getItem(this.filterApplicationsMapProcessingStatus_cache_name) ? sessionStorage.getItem(this.filterApplicationsMapProcessingStatus_cache_name) : 'all';
                this.filterApplicationsMapLodgedFrom = sessionStorage.getItem(this.filterApplicationsMapLodgedFrom_cache_name) ? sessionStorage.getItem(this.filterApplicationsMapLodgedFrom_cache_name) : '';
                this.filterApplicationsMapLodgedTo = sessionStorage.getItem(this.filterApplicationsMapLodgedTo_cache_name) ? sessionStorage.getItem(this.filterApplicationsMapLodgedTo_cache_name) : '';
            })
        },
        applyFiltersFrontEnd: function () {
            this.filteredProposals = [...this.proposals];
            console.log('applyFiltersFrontEnd', this.filteredProposals)
            console.log('this.filteredProposals', this.filteredProposals)
            console.log('this.filterApplicationsMapApplicationType', this.filterApplicationsMapApplicationType)
            console.log('this.filterApplicationsMapApplicationType typeof', typeof this.filterApplicationsMapApplicationType)
            if ('all' != this.filterApplicationsMapApplicationType) {
                this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.application_type_id == this.filterApplicationsMapApplicationType)]
                console.log('this.filteredProposals', this.filteredProposals)
            }
            if ('all' != this.filterApplicationsMapProcessingStatus) {
                this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.processing_status == this.filterApplicationsMapProcessingStatus)]
            }
            if ('' != this.filterApplicationsMapLodgedFrom) {
                this.filteredProposals = [...this.filteredProposals.filter(proposal => new Date(proposal.lodgement_date) >= new Date(this.filterApplicationsMapLodgedFrom))]
            }
            if ('' != this.filterApplicationsMapLodgedTo) {
                this.filteredProposals = [...this.filteredProposals.filter(proposal => new Date(proposal.lodgement_date) >= new Date(this.filterApplicationsMapLodgedTo))]
            }
            this.loadFeatures(this.filteredProposals);
        },
        valueChanged: function (value, tileLayer) {
            tileLayer.setOpacity(value / 100)
        },
        download_content: function (content, fileName, contentType) {
            var a = document.createElement("a");
            var file = new Blob([content], { type: contentType });
            a.href = URL.createObjectURL(file);
            a.download = fileName;
            a.click();
        },
        geoJsonButtonClicked: function () {
            let vm = this
            let json = new GeoJSON().writeFeatures(vm.modelQuerySource.getFeatures(), {})
            vm.download_content(json, 'leases_and_licensing_layers.geojson', 'text/plain');
        },
        displayAllFeatures: function () {
            console.log('in displayAllFeatures()')
            let vm = this
            if (vm.map) {
                if (vm.modelQuerySource.getFeatures().length > 0) {
                    let view = vm.map.getView()
                    let ext = vm.modelQuerySource.getExtent()
                    let centre = [(ext[0] + ext[2]) / 2.0, (ext[1] + ext[3]) / 2.0]
                    let resolution = view.getResolutionForExtent(ext);
                    let z = view.getZoomForResolution(resolution) - 1
                    view.animate({ zoom: z, center: centre })
                }
            }
        },
        setBaseLayer: function (selected_layer_name) {
            let vm = this
            if (selected_layer_name == 'sat') {
                vm.tileLayerMapbox.setVisible(false)
                vm.tileLayerSat.setVisible(true)
                $('#basemap_sat').hide()
                $('#basemap_osm').show()
            } else {
                vm.tileLayerMapbox.setVisible(true)
                vm.tileLayerSat.setVisible(false)
                $('#basemap_osm').hide()
                $('#basemap_sat').show()
            }
        },
        changeLayerVisibility: function (targetLayer) {
            targetLayer.setVisible(!targetLayer.getVisible())
        },
        clearMeasurementLayer: function () {
            let vm = this
            let features = vm.measurementLayer.getSource().getFeatures()
            features.forEach((feature) => {
                vm.measurementLayer.getSource().removeFeature(feature)
            })
        },
        forceToRefreshMap() {
            let vm = this
            setTimeout(function () {
                vm.map.updateSize();
            }, 700)
        },
        addJoint: function (point, styles) {
            let s = new Style({
                image: new CircleStyle({
                    radius: 2,
                    fill: new Fill({
                        color: '#3399cc',
                    }),
                }),
            })
            s.setGeometry(point)
            styles.push(s)

            return styles
        },
        /**
         * Returns a color for a feature based on the styleBy property
         * and either the feature or model object
         * @param {dict} featureData A feature object
         * @param {Proxy} model A model object
         */
        styleByColor: function(featureData, model) {
            let vm = this;

            if (vm.styleBy === 'assessor') {
                // Assume the object is a feature containing a polygon_source property
                return vm.featureColors[featureData.properties.polygon_source.toLowerCase()];
            } else if (vm.styleBy === 'model') {
                // Assume the object is a model containing a color field
                return model.color;
            } else {
                return vm.featureColors["unknown"] || vm.defaultColor;
            }
        },
        createStyle: function(color) {
            let vm = this;
            if (!color) {
                color = vm.defaultColor;
            }

            let style = new Style({
                stroke: new Stroke({
                    color: color,
                    width: 1,
                }),
                fill: new Fill({
                    color: color,
                }),
            });

            return style;
        },
        styleFunctionForMeasurement: function (feature, resolution) {
            let vm = this
            let for_layer = feature.get('for_layer', false)

            const styles = []
            styles.push(vm.style)  // This style is for the feature itself
            styles.push(vm.segmentStyle)

            ///////
            // From here, adding labels and tiny circles at the end points of the linestring
            ///////
            const geometry = feature.getGeometry();
            if (geometry.getType() === 'LineString') {
                let segment_count = 0;
                geometry.forEachSegment(function (a, b) {
                    const segment = new LineString([a, b]);
                    const label = formatLength(segment);
                    const segmentPoint = new Point(segment.getCoordinateAt(0.5));

                    // Add a style for this segment
                    let segment_style = vm.segmentStyle.clone() // Because there could be multilpe segments, we should copy the style per segment
                    segment_style.setGeometry(segmentPoint)
                    segment_style.getText().setText(label)
                    styles.push(segment_style)

                    if (segment_count == 0) {
                        // Add a tiny circle to the very first coordinate of the linestring
                        let p = new Point(a)
                        vm.addJoint(p, styles)
                    }
                    // Add tiny circles to the end of the linestring
                    let p = new Point(b)
                    vm.addJoint(p, styles)

                    segment_count++;
                });
            }

            if (!for_layer) {
                // We don't need the last label when draw on the layer.
                let label_on_mouse = formatLength(geometry);  // Total length of the linestring
                let point = new Point(geometry.getLastCoordinate());
                vm.labelStyle.setGeometry(point);
                vm.labelStyle.getText().setText(label_on_mouse);
                styles.push(vm.labelStyle);
            }

            return styles
        },
        initialiseMap: function () {
            let vm = this;

            let satelliteTileWms = new TileWMS({
                url: env['kmi_server_url'] + '/geoserver/public/wms',
                params: {
                    'FORMAT': 'image/png',
                    'VERSION': '1.1.1',
                    tiled: true,
                    STYLES: '',
                    LAYERS: 'public:mapbox-satellite',
                }
            });

            let streetsTileWMS = new TileWMS({
                url: env['kmi_server_url'] + '/geoserver/public/wms',
                params: {
                    'FORMAT': 'image/png',
                    'VERSION': '1.1.1',
                    tiled: true,
                    STYLES: '',
                    LAYERS: `public:${baselayer_name}`
                }
            });
            vm.tileLayerMapbox = new TileLayer({
                title: 'StreetsMap',
                type: 'base',
                visible: true,
                source: streetsTileWMS,
            })

            vm.tileLayerSat = new TileLayer({
                title: 'Satellite',
                type: 'base',
                visible: true,
                source: satelliteTileWms,
            })

            vm.map = new Map({
                layers: [
                    vm.tileLayerMapbox,
                    vm.tileLayerSat,
                ],
                target: vm.elem_id,
                view: new View({
                    center: [115.95, -31.95],
                    zoom: 7,
                    projection: 'EPSG:4326'
                })
            });

            // Full screen toggle
            let fullScreenControl = new FullScreenControl()
            vm.map.addControl(fullScreenControl)

            vm.initialiseMeasurementLayer()
            vm.initialiseQueryLayer()
            vm.initialiseDrawLayer()

            // update map extent when new features added
            vm.map.on('rendercomplete', vm.fitToLayer);

            vm.initialisePointerMoveEvent();
            vm.initialiseSelectFeatureEvent();
            vm.initialiseSingleClickEvent();
            vm.initialiseDoubleClickEvent();
        },
        initialiseMeasurementLayer: function () {
            let vm = this;

            // Measure tool
            let draw_source = new VectorSource({ wrapX: false })
            vm.drawForMeasure = new Draw({
                source: draw_source,
                type: 'LineString',
                style: vm.styleFunctionForMeasurement,
            })
            // Set a custom listener to the Measure tool
            vm.drawForMeasure.set('escKey', '')
            vm.drawForMeasure.on('change:escKey', function (evt) {
            })
            vm.drawForMeasure.on('drawstart', function (evt) {
                // Set measuring to true on mode change (fn `set_mode`), not drawstart
            })
            vm.drawForMeasure.on('drawend', function (evt) {
                // Set measuring to false on mode change
            })

            // Create a layer to retain the measurement
            vm.measurementLayer = new VectorLayer({
                title: 'Measurement Layer',
                source: draw_source,
                style: function (feature, resolution) {
                    feature.set('for_layer', true)
                    return vm.styleFunctionForMeasurement(feature, resolution)
                },
            });
            vm.map.addInteraction(vm.drawForMeasure)
            vm.map.addLayer(vm.measurementLayer)
        },
        initialiseQueryLayer: function () {
            let vm = this;

            vm.modelQuerySource = new VectorSource({});
            const style = new Style({
                fill: new Fill({
                    color: vm.defaultColor,
                }),
            });

            vm.modelQueryLayer = new VectorLayer({
                title: "Model Area of Interest",
                name: "query_layer",
                source: vm.modelQuerySource,
                style: function (feature) {
                    const color = feature.get('color') || vm.defaultColor;
                    style.getFill().setColor(color);
                    return style;
                },
            });
            // Add the layer
            vm.map.addLayer(vm.modelQueryLayer);
            // Set zIndex to some layers to be rendered over the other layers
            vm.modelQueryLayer.setZIndex(10);
        },
        initialiseDrawLayer: function () {
            let vm = this;
            if (!vm.drawable){
                return;
            }

            vm.drawForModel = new Draw({
                source: vm.modelQuerySource,
                type: 'Polygon',
                geometryFunction: function (coordinates, geometry) {
                    if (geometry) {
                        if (coordinates[0].length) {
                            // Add a closing coordinate to match the first
                            geometry.setCoordinates(
                                [coordinates[0].concat([coordinates[0][0]])],
                                this.geometryLayout_
                            );
                        } else {
                            geometry.setCoordinates([], this.geometryLayout_);
                        }

                    } else {
                        geometry = new Polygon(coordinates, this.geometryLayout_);
                    }
                    vm.sketchCoordinates = coordinates[0].slice();
                    if (coordinates[0].length > vm.sketchCoordinatesHistory.length) {
                        // Only reassign the sketchCoordinatesHistory if the new coordinates are longer than the previous
                        // so we don't lose the history when the user undoes a point
                        vm.sketchCoordinatesHistory = coordinates[0].slice();
                    }

                    return geometry;
                },
                condition: function(evt) {
                    if (evt.originalEvent.buttons === 1) {
                        // Only allow drawing when the left mouse button is pressed
                        return true;
                    } else if (evt.originalEvent.buttons === 2) {
                        // If the right mouse button is pressed, undo the last point
                        if (vm.showUndoButton) {
                            vm.undoLeaseLicensePoint();
                        } else {
                            vm.set_mode('layer');
                        }
                    } else {
                        return false;
                    }
                },
                finishCondition: function (evt) {
                    if (vm.lastPoint) {
                        vm.$emit('validate-feature');
                    }
                    return false;
                },
            })
            vm.drawForModel.set('escKey', '')
            vm.drawForModel.on('change:escKey', function (evt) {
                console.log("ESC key pressed");
            })
            vm.drawForModel.on('drawstart', function () {
                vm._errorMessage = null;
                vm.lastPoint = null;
            });
            vm.drawForModel.on('click'), function (evt) {
                console.log(evt);
            }
            vm.drawForModel.on('drawend', function (evt) {
                console.log(evt);
                console.log(evt.feature.values_.geometry.flatCoordinates);
                let model = vm.context || {};

                let color = vm.featureColors["draw"] ||
                            vm.featureColors["unknown"] ||
                            vm.defaultColor;
                evt.feature.setProperties({
                    id: vm.newFeatureId,
                    model: model,
                    polygon_source: "New",
                    name: model.id || -1,
                    // FIXME: Can this be standardised into the same field name?
                    label: model.label || model.application_type_name_display || (model.application_type? model.application_type.name_display: undefined) || "Draw",
                    color: color,
                })
                vm.newFeatureId++;
                console.log('newFeatureId = ' + vm.newFeatureId);
                vm.lastPoint = evt.feature;
                vm.sketchCoordinates = [[]];
                vm.sketchCoordinatesHistory = [[]];
            });
            vm.map.addInteraction(vm.drawForModel);
        },
        initialisePointerMoveEvent: function () {
            let vm = this

            const hoverStyle = new Style({
                fill: vm.hoverFill,
                stroke: vm.hoverStroke,
            });
            // Cache the hover fill so we don't have to create a new one every time
            // Also prevent overwriting property `hoverFill` color
            let _hoverFill = null;
            function hoverSelect(feature) {
                const color = feature.get('color') || vm.defaultColor;
                _hoverFill = new Fill({color: color});

                // If the feature is already selected, use the select stroke when hovering
                if (vm.selectedFeatureIds.includes(feature.getProperties().id)) {
                    hoverStyle.setFill(_hoverFill);
                    hoverStyle.setStroke(vm.clickSelectStroke);
                } else {
                    hoverStyle.setFill(vm.hoverFill);
                    hoverStyle.setStroke(vm.hoverStroke);
                }
                return hoverStyle;
            }

            let selected = null;
            vm.map.on('pointermove', function (evt) {
                if (vm.measuring || vm.drawing) {
                    // Don't highlight features when measuring or drawing
                    return;
                }
                if (selected !== null) {
                    if (vm.selectedFeatureIds.includes(selected.getProperties().id)) {
                        // Don't alter style of click-selected features
                        console.log("ignoring hover on selected feature");
                    } else {
                        selected.setStyle(undefined);
                        selected.setStyle(vm.createStyle(selected.values_.color));
                    }
                    selected = null;
                }
                vm.map.forEachFeatureAtPixel(evt.pixel, function (feature, layer) {
                    selected = feature;
                    let model = selected.getProperties().model
                    if (!model) {
                        console.error("No model found for feature");
                    } else {
                        model.polygon_source = selected.getProperties().polygon_source;
                    }
                    vm.selectedModel = model
                    selected.setStyle(hoverSelect);
                }, {layerFilter: function (layer) {
                        return layer.get('name') === 'query_layer';
                    }
                });
                if (selected) {
                    vm.featureToast.show()
                } else {
                    vm.featureToast.hide()
                }
            });
        },
        initialiseSingleClickEvent: function () {
            let vm = this;
            vm.map.on('singleclick', function(evt) {
                if (vm.drawing || vm.measuring) {
                    console.log(evt);
                    // TODO: must be a feature
                    vm.lastPoint = new Point(evt.coordinate);
                    return;
                }

                let feature = vm.map.forEachFeatureAtPixel(evt.pixel, function (feature, layer) {
                    return feature;
                });
                if (feature) {
                    vm.map.getInteractions().forEach((interaction) => {
                        if (interaction instanceof Select) {
                            let selected = [];
                            let deselected = [];
                            let feature_id = feature.get("id");
                            if (vm.selectedFeatureIds.includes(feature_id)) {
                                // already selected, so deselect
                                deselected.push(feature);
                            } else {
                                // not selected, so select
                                selected.push(feature);
                            }
                            interaction.dispatchEvent({
                                type: 'select',
                                selected: selected,
                                deselected: deselected,
                            });
                        }
                    });
                }
            });
        },
        initialiseDoubleClickEvent: function () {
            let vm = this
            vm.map.on('dblclick', function (evt) {
                vm.redirectingToModelDetails = true;
                evt.stopPropagation();

                let feature = vm.map.forEachFeatureAtPixel(evt.pixel, function (feature, layer) {
                    return feature;
                });
                if (feature) {
                    let model = feature.getProperties().model
                    if (!model) {
                        vm.redirectingToModelDetails = false;
                        return;
                    }

                    // TODO: Return path from serializer
                    let model_path = model.details_url;
                    // Remove trailing slash from urls
                    let pathnames = [window.location.pathname, model.details_url]
                    for (let i = 0; i < pathnames.length; i++) {
                        let path_name = pathnames[i];
                        if (path_name[path_name.length - 1] === '/') {
                            path_name = path_name.slice(0, -1);
                        }
                        pathnames[i] = path_name;
                    }
                    // array remove duplicates
                    pathnames = [...new Set(pathnames)];
                    if (pathnames.length === 1) {
                        console.log('already on model details page');
                        vm.redirectingToModelDetails = false;
                    } else {
                        window.location = model_path;
                    }
                } else {
                    vm.redirectingToModelDetails = false;
                }
            });
        },
        initialiseSelectFeatureEvent: function () {
            let vm = this;
            if (!vm.selectable) {
                return;
            }

            const clickSelectStyle = new Style({
                fill: new Fill({
                    color: '#000000',
                }),
                stroke: vm.clickSelectStroke,
            });

            function clickSelect(feature) {
                // Keep feature fill color but change stroke color
                const color = feature.get('color') || vm.defaultColor;
                clickSelectStyle.getFill().setColor(color);
                return clickSelectStyle;
            }

            // select interaction working on "singleclick"
            const selectSingleClick = new Select({
                style: clickSelect,
                layers: [vm.modelQueryLayer,],
            });
            vm.map.addInteraction(selectSingleClick);
            selectSingleClick.on('select', (evt) => {
                $.each(evt.selected, function (idx, feature) {
                    console.log(`Selected feature ${feature.getProperties().id}`,
                        toRaw(feature));
                    feature.setStyle(clickSelect);
                    vm.selectedFeatureIds.push(feature.getProperties().id);
                });

                $.each(evt.deselected, function (idx, feature) {
                    console.log(`Unselected feature ${feature.getProperties().id}`);
                    feature.setStyle(undefined);
                    vm.selectedFeatureIds = vm.selectedFeatureIds.filter(
                        id => id != feature.getProperties().id);
                });
            });
        },
        undoLeaseLicensePoint: function () {
            let vm = this;
            console.log(vm.drawForModel.sketchCoords_)
            if (vm.lastPoint) {
                vm.modelQuerySource.removeFeature(vm.lastPoint);
                vm.lastPoint = null;
                vm.sketchCoordinates = [[]]
                vm.sketchCoordinatesHistory = [[]]
                this.selectedFeatureId = null;
            } else {
                vm.drawForModel.removeLastPoint();
            }
        },
        redoLeaseLicensePoint: function () {
            let vm = this;
            if (vm.sketchCoordinatesHistory.length > vm.sketchCoordinates.length) {
                let nextCoordinate = vm.sketchCoordinatesHistory.slice(vm.sketchCoordinates.length, vm.sketchCoordinates.length + 1);
                vm.drawForLeaselicence.appendCoordinates([nextCoordinate[0]]);
            }
        },
        removeModelFeatures: function () {
            let vm = this;
            const features = vm.modelQuerySource.getFeatures().filter((feature) => {
                if (vm.selectedFeatureIds.includes(feature.getProperties().id)) {
                    return feature;
                }
            });

            for (let feature of features) {
                vm.modelQuerySource.removeFeature(feature);
            }
            // Remove selected features (mapped by id) from `selectedFeatureIds`
            vm.selectedFeatureIds = vm.selectedFeatureIds.filter(
                id => !features.map(
                    feature => feature.getProperties().id
                    ).includes(id));
        },
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
        },
        fetchProposals: async function () {
            let vm = this
            let url = api_endpoints.proposal + 'list_for_map/'
            if (vm.proposalIds.length > 0) {
                url += '?proposal_ids=' + vm.proposalIds.toString();
            }
            if (vm.filterApplicationsMapApplicationType != 'all') {
                url += '?application_type=' + vm.filterApplicationsMapApplicationType
            }
            if (vm.filterApplicationsMapApplicationType != 'all') {
                url += '?application_type=' + vm.filterApplicationsMapApplicationType
            }
            fetch(url)
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    vm.proposals = data
                    vm.filteredProposals = [...vm.proposals]
                    vm.assignProposalFeatureColors(vm.proposals);
                    vm.loadFeatures(vm.proposals);
                    vm.applyFiltersFrontEnd();
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
        },
        fetchFilterLists: function () {
            let vm = this;

            // Application Types
            fetch(api_endpoints.application_types + 'key-value-list/').then(async (response) => {
                const resData = await response.json()
                vm.application_types = resData
            }, (error) => {
            })

            // Application Statuses
            fetch(api_endpoints.application_statuses_dict + '?for_filter=true').then(async (response) => {
                const resData = await response.json()
                vm.processing_statuses = resData
            }, (error) => {
            })
        },
        addFeatureCollectionToMap: function(featureCollection) {
            let vm = this;
            if (featureCollection == null) {
                featureCollection = vm.featureCollection;
            }

            for (let featureData of vm.featureCollection["features"]) {
                let feature = vm.featureFromDict(featureData, featureData.model);

                vm.modelQuerySource.addFeature(feature);
                vm.newFeatureId++;
            };
        },
        assignProposalFeatureColors: function (proposals) {
            let vm = this;
            proposals.forEach(function (proposal) {
                proposal.color = vm.getRandomRGBAColor();
                console.log(proposal.lodgement_date)
                console.log(typeof proposal.lodgement_date)
            });
        },
        loadFeatures: function (proposals) {
            let vm = this;
            console.log(proposals)
            // Remove all features from the layer
            vm.modelQuerySource.clear();
            proposals.forEach(function (proposal) {
                proposal.proposalgeometry.features.forEach(function (featureData) {

                    let feature = vm.featureFromDict(featureData, proposal);
                    vm.modelQuerySource.addFeature(feature);
                    vm.newFeatureId++;
                });
            });

            vm.addFeatureCollectionToMap();
        },
        /**
         * Creates a styled feature object from a feature dictionary
         * @param {dict} featureData A feature dictionary
         * @param {Proxy} model A model object
         */
        featureFromDict: function (featureData, model) {
            let vm = this;
            if (model == null) {
                model = {};
            }

            let color = vm.styleByColor(featureData, model);
            let style = vm.createStyle(color);

            let feature = new Feature({
                id: vm.newFeatureId, // Incrementing-id of the polygon/feature on the map
                geometry: new Polygon(featureData.geometry.coordinates),
                name: model.id,
                label: model.label || model.application_type_name_display,
                color: color,
                source: featureData.properties.source,
                polygon_source: featureData.properties.polygon_source
            });
            // Id of the model object (https://datatracker.ietf.org/doc/html/rfc7946#section-3.2)
            feature.setId(featureData.id);

            feature.setProperties({
                model: model,
            });
            feature.setStyle(style);

            return feature;
        },
        getProposalById: function (id) {
            return this.proposals.find(proposal => proposal.id === id);
        },
        getRandomColor: function () {
            let letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() *
                    16)];
            }
            return color;
        },
        getRandomRGBAColor: function () {
            var o = Math.round, r = Math.random, s = 255;
            return [o(r() * s), o(r() * s), o(r() * s), 0.5];
        },
        getJSONFeatures: function () {
            const format = new GeoJSON();
            const features = this.modelQuerySource.getFeatures();

            features.forEach(function (feature) {
                console.log(feature.getProperties());
                // feature.unset("model")
            });

            return format.writeFeatures(features);
        },
        /**
         * Returns a dictionary of query parameters for a given layer
         * @param {String} layerStr The dictionary key containing the layer information
         */
        queryParamsDict: function(layerStr) {
            let vm = this;

            if (!layerStr in vm.owsQuery) {
                console.error(`Layer ${layerStr} not found in OWS query`);
                return {};
            }
            if (!vm.owsQuery[layerStr].typeName) {
                console.error(`Layer ${layerStr} needs a typeName`);
                return {};
            }

            return {
                "service": vm.owsQuery.service || "WFS",
                "version": vm.owsQuery.version || "1.0.0",
                "request": vm.owsQuery[layerStr].request || "GetFeature",
                "typeName": vm.owsQuery[layerStr].typeName,
                "maxFeatures": vm.owsQuery[layerStr].maxFeatures || "5000",
                "srsName": vm.owsQuery[layerStr].srsName || "EPSG:4326",
                "outputFormat": vm.owsQuery[layerStr].outputFormat || "application/json",
                "propertyName": vm.owsQuery[layerStr].propertyName || "wkb_geometry",
            }
        },
        /**
         * Returns a Well-known-text (WKT) representation of a feature
         * @param {Feature} feature A feature to validate
         */
        featureToWKT: function (feature) {
            let vm = this;

            if (feature === undefined) {
                // If no feature is provided, create a feature from the current sketch
                let coordinates = vm.sketchCoordinates.slice();
                coordinates.push(coordinates[0]);
                feature = new Feature({
                    id: -1,
                    geometry: new Polygon([coordinates]),
                    label: "validation",
                    color: vm.defaultColor,
                    polygon_source: "validation",
                });
            }

            // Prepare a WFS feature intersection request
            let flatCoordinates = feature.values_.geometry.flatCoordinates;

            // Transform list of flat coordinates into a list of coordinate pairs,
            // e.g. ['x1 y1', 'x2 y2', 'x3 y3']
            let flatCoordinateStringPairs = flatCoordinates.map((coord, index) => index % 2 == 0 ?
                    [flatCoordinates[index], flatCoordinates[index + 1]].join(" ") :
                        "")
                    .filter(item => item != "")

            // Create a Well-Known-Text polygon string from the coordinate pairs
            return `POLYGON ((${flatCoordinateStringPairs.join(", ")}))`;
        },
        /**
         * Validates an openlayers feature against a geoserver `url`.
         * @param {Feature} feature A feature to validate
         * @returns {Promise} A promise that resolves to a list of intersected features
         */
        validateFeatureQuery: async function (query) {
            let vm = this;

            let features = [];
            // Query the WFS
            vm.queryingGeoserver = true;
            // var urls = [`${url}${params}`];
            var urls = [query];

            var requests = urls.map(url => utils.fetchUrl(url).then(response => response));
            await Promise.all(requests).then((data) => {
                features = new GeoJSON().readFeatures(data[0]);
            }).catch((error) => {
                console.log(error.message);
                vm._errorMessage = error.message;
            });

            return features;
        },
        /**
         * Finish drawing of the current feature sketch.
         */
        finishDrawing: function () {
            let vm = this;
            vm.queryingGeoserver = false;
            vm._errorMessage = null;
            vm.drawForModel.finishDrawing()
        },
        /**
         * Returns the current error message or sets it to the provided message.
         * @param {String} message The new error message
         */
        errorMessage: function (message) {
            let vm = this;
            if (message === undefined) {
                return vm._errorMessage;
            }

            vm.queryingGeoserver = false;

            if (vm._errorMessage === null) {
                vm._errorMessage = message;
            }
        },
    },
    created: function () {
        console.log('created()')
        this.fetchFilterLists();
        this.fetchProposals();
    },
    mounted: function () {
        console.log('mounted()')
        let vm = this;

        this.$nextTick(() => {
            vm.initialiseMap()
            set_mode.bind(this)("layer")
            vm.setBaseLayer('osm')
            addOptionalLayers(this)
            var toastEl = document.getElementById('featureToast');
            vm.featureToast = new bootstrap.Toast(toastEl, { autohide: false });
        });
    }
}
</script>
<style scoped>
@import '../../../../../static/leaseslicensing/css/map.css';


#featureToast {
    position: absolute;
    bottom: 10px;
    left: 10px;
}

.close-icon:hover {
    filter: brightness(80%);
}

.close-icon {
    position: absolute;
    left: 1px;
    top: -11px;
    filter: drop-shadow(0 1px 4px rgba(0, 0, 0, 0.2));
}

.popup-wrapper {
    padding: 0.25em;
}

.popup-content-header {
    background: darkgray;
    color: white;
}

.popup-content {
    font-size: small;
}

.table_caption {
    color: green;
}

.filter_search_wrapper {
    position: relative;
    z-index: 10;
}

.table_apiary_site {
    position: relative;
    z-index: 10;
}

.button_row {
    display: flex;
    justify-content: flex-end;
}

.view_all_button {
    color: #03a9f4;
    cursor: pointer;
}

.status_filter_dropdown_wrapper {
    position: relative;
}

.status_filter_dropdown_button {
    cursor: pointer;
    width: 100%;
    position: relative;
}

.status_filter_dropdown {
    position: absolute;
    background: white;
    display: none;
    border-radius: 2px;
    min-width: max-content;
    padding: 0.5em;
    border: 3px solid rgba(5, 5, 5, .1);
}

.sub_option {
    margin-left: 1em;
}

.dropdown_arrow::after {
    content: "";
    width: 7px;
    height: 7px;
    border: 0px;
    border-bottom: solid 2px #909090;
    border-right: solid 2px #909090;
    -ms-transform: rotate(45deg);
    -webkit-transform: rotate(45deg);
    transform: rotate(45deg);
    position: absolute;
    top: 50%;
    right: 21px;
    margin-top: -4px;
}

/*
    .status_filter_dropdown {
        position: absolute;
        display: none;
        background: white;
        padding: 1em;
    }
    */
.select2-container {
    z-index: 100000;
}

.select2-options {
    z-index: 100000;
}

.dataTables_filter {
    display: none !important;
}

.badge {
  padding-left: 9px;
  padding-right: 9px;
  -webkit-border-radius: 9px;
  -moz-border-radius: 9px;
  border-radius: 9px;
}

.label-warning[href],
.badge-warning[href] {
  background-color: #c67605;
}
#selectedFeatureCount {
    font-size: 12px;
    background: #ff0000;
    color: #fff;
    padding: 0 5px;
    vertical-align: top;
    margin-left: -10px;
}
</style>
