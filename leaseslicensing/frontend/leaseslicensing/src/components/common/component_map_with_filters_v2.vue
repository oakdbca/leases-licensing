<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="collapsible_filters" @created="collapsible_component_mounted"
            class="mb-2">
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
                </div>

                <div id="featureToast" class="toast" style="z-index:9999">
                    <template v-if="selectedProposal">
                        <div class="toast-header">
                            <img src="" class="rounded me-2" alt="">
                            <strong class="me-auto">Application: {{ selectedProposal.lodgement_number }}</strong>
                        </div>
                        <div class="toast-body">
                            <table class="table table-sm">
                                <tbody>
                                    <tr>
                                        <th scope="row">Application Type</th>
                                        <td>{{ selectedProposal.application_type_name_display }}</td>
                                    </tr>
                                    <tr>
                                        <th scope="row">Processing Status</th>
                                        <td>{{ selectedProposal.processing_status_display }}</td>
                                    </tr>
                                    <tr v-if="selectedProposal.lodgement_date_display">
                                        <th scope="row">Lodgement Date</th>
                                        <td>{{ selectedProposal.lodgement_date_display
                                        }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </template>
                </div>

            </div>
            <BootstrapSpinner v-if="!proposals" class="text-primary" />
            <BootstrapSpinner v-if="redirectingToProposalDetails" class="text-primary" />

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
        <div class="debug">
            <div v-if="filteredProposals">filtered proposals length: {{ filteredProposals.length }}</div>
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid';
import { api_endpoints, helpers, constants } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'

import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import TileWMS from 'ol/source/TileWMS';
import { Draw } from 'ol/interaction';
import Feature from 'ol/Feature'
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import { FullScreen as FullScreenControl } from 'ol/control';
import { LineString, Point, Polygon } from 'ol/geom';
import GeoJSON from 'ol/format/GeoJSON';
import MeasureStyles, { formatLength } from '@/components/common/measure.js'
import RangeSlider from '@/components/forms/range_slider.vue'
import { addOptionalLayers, set_mode, baselayer_name } from '@/components/common/map_functions.js'

export default {
    name: 'MapComponentWithFiltersV2',
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
            default: 'filterApplicationsMapApplicationType',
        },
        filterApplicationsMapProcessingStatus_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationsMapProcessingStatus',
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
            measurementLayer: null,
            style: MeasureStyles.defaultStyle,
            segmentStyle: MeasureStyles.segmentStyle,
            labelStyle: MeasureStyles.labelStyle,
            segmentStyles: null,
            content_element: null,
            featureToast: null,
            selectedFeature: null,
            selectedProposal: null,
            redirectingToProposalDetails: false,
            proposals: null,
            filteredProposals: [],
            proposalQuerySource: null,
            proposalQueryLayer: null,
            set_mode: set_mode
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
    },
    components: {
        CollapsibleFilters,
        RangeSlider,
        helpers,
    },
    watch: {
        filterApplicationsMapApplicationType: function () {
            console.log('filterApplicationsMapApplicationType', this.filterApplicationsMapApplicationType)
            this.applyFiltersFrontEnd();
            sessionStorage.setItem(this.filterApplicationsMapApplicationType_cache_name, this.filterApplicationsMapApplicationType);
        },
        filterApplicationsMapProcessingStatus: function () {
            this.applyFiltersFrontEnd();
            sessionStorage.setItem(this.filterApplicationsMapProcessingStatus_cache_name, this.filterApplicationsMapProcessingStatus);
        },
        filterApplicationsMapLodgedFrom: function () {
            this.applyFiltersFrontEnd();
            sessionStorage.setItem('filterApplicationsMapLodgedFromForMap', this.filterApplicationsMapLodgedFrom);
        },
        filterApplicationsMapLodgedTo: function () {
            this.applyFiltersFrontEnd();
            sessionStorage.setItem('filterApplicationsMapLodgedToForMap', this.filterApplicationsMapLodgedTo);
        },
        filterApplied: function () {
            if (this.$refs.collapsible_filters) {
                // Collapsible component exists
                this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
            }
        },

    },
    methods: {
        applyFiltersFrontEnd: function () {
            this.filteredProposals = [...this.proposals];
            if ('all' != this.filterApplicationsMapApplicationType) {
                this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.application_type_id === this.filterApplicationsMapApplicationType)]
            }
            if ('all' != this.filterApplicationsMapProcessingStatus) {
                this.filteredProposals = [...this.filteredProposals.filter(proposal => proposal.processing_status === this.filterApplicationsMapProcessingStatus)]
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
            let json = new GeoJSON().writeFeatures(vm.proposalQuerySource.getFeatures(), {})
            vm.download_content(json, 'leases_and_licensing_layers.geojson', 'text/plain');
        },
        displayAllFeatures: function () {
            console.log('in displayAllFeatures()')
            let vm = this
            if (vm.map) {
                if (vm.proposalQuerySource.getFeatures().length > 0) {
                    let view = vm.map.getView()
                    let ext = vm.proposalQuerySource.getExtent()
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
        initMap: function () {
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
                vm.measuring = true
            })
            vm.drawForMeasure.on('drawend', function (evt) {
                vm.measuring = false
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

            vm.proposalQuerySource = new VectorSource({});

            const style = new Style({
                fill: new Fill({
                    color: '#eeeeee',
                }),
            });

            vm.proposalQueryLayer = new VectorLayer({
                source: vm.proposalQuerySource,
                style: function (feature) {
                    const color = feature.get('color') || '#eeeeee';
                    style.getFill().setColor(color);
                    return style;
                },
            });
            vm.map.addLayer(vm.proposalQueryLayer);

            vm.initialisePointerMoveEvent();
            vm.initialiseDoubleClickEvent();
        },
        initialisePointerMoveEvent: function () {
            let vm = this

            const selectStyle = new Style({
                fill: new Fill({
                    color: 'rgba(255, 255, 255, 0.5)',
                }),
                stroke: new Stroke({
                    color: 'rgba(255, 255, 255, 0.5)',
                    width: 1,
                }),
            });
            let selected = null;
            vm.map.on('pointermove', function (evt) {
                if (selected !== null) {
                    selected.setStyle(undefined);
                    selected = null;
                }
                vm.map.forEachFeatureAtPixel(evt.pixel, function (feature, layer) {
                    selected = feature;
                    let proposal = selected.getProperties().proposal
                    vm.selectedProposal = proposal
                    selected.setStyle(selectStyle);
                });
                if (selected) {
                    vm.featureToast.show()
                } else {
                    vm.featureToast.hide()
                }
            });
        },
        initialiseDoubleClickEvent: function () {
            let vm = this
            vm.map.on('dblclick', function (evt) {
                vm.redirectingToProposalDetails = true;
                evt.stopPropagation();

                let feature = vm.map.forEachFeatureAtPixel(evt.pixel, function (feature, layer) {
                    return feature;
                });
                if (feature) {
                    let proposal = feature.getProperties().proposal
                    window.location = '/internal/proposal/' + proposal.id
                }
            });
        },
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
        },
        fetchProposals: async function () {
            let vm = this
            let url = api_endpoints.proposal + 'list_for_map/'
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
            vm.proposalQuerySource.clear();
            proposals.forEach(function (proposal) {
                let style = new Style({
                    stroke: new Stroke({
                        color: proposal.color,
                        width: 1,
                    }),
                    fill: new Fill({
                        color: proposal.color,
                    }),
                });
                proposal.proposalgeometry.features.forEach(function (featureData) {
                    let feature = new Feature({
                        geometry: new Polygon(featureData.geometry.coordinates),
                        name: proposal.id,
                        label: proposal.application_type_name_display,
                        color: proposal.color,
                    });
                    feature.setStyle(style)
                    feature.setProperties({
                        proposal: proposal,
                    })
                    vm.proposalQuerySource.addFeature(feature);
                });
            });
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
            vm.initMap()
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
</style>
