<template>
    <div>
        <div class="map-wrapper row col-sm-12 mb-1">
            <!--div id='popup-container'>
                <p id='popup-coordinates'></p>
            </div-->
            <div :id="elem_id" ref="map-root" class="map">
                <div class="basemap-button">
                    <img v-if="showSatIcon" id="basemap_sat" src="../../assets/satellite_icon.jpg"
                        @click="setBaseLayer('sat')" />
                    <img v-if="!showSatIcon" id="basemap_osm" src="../../assets/map_icon.png"
                        @click="setBaseLayer('osm')" />
                </div>
                <div class="optional-layers-wrapper">
                    <div class="optional-layers-button-wrapper">
                        <div :class="[
                            mode == 'measure' ? 'optional-layers-button-active' : 'optional-layers-button'
                        ]" @click="set_mode.bind(this)('measure')">
                            <img class="svg-icon" src="../../assets/ruler.svg" />
                        </div>
                    </div>
                    <div class="optional-layers-button-wrapper">
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
                    <div v-if="selectedFeatureId" class="optional-layers-button-wrapper">
                        <div class="optional-layers-button">
                            <i id="delete_feature" class="svg-icon bi bi-trash3 ll-trash"
                                @click="removeLeaselicenceFeature()" />
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
            </div>
        </div>
        <div :id="popup_id" class="ol-popup">
            <a href="#" :id="popup_closer_id" class="ol-popup-closer">
                <svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='20' width='20' class="close-icon">
                    <g transform='scale(3)'>
                        <path
                            d="M 5.2916667,2.6458333 A 2.6458333,2.6458333 0 0 1 2.6458335,5.2916667 2.6458333,2.6458333 0 0 1 0,2.6458333 2.6458333,2.6458333 0 0 1 2.6458335,0 2.6458333,2.6458333 0 0 1 5.2916667,2.6458333 Z"
                            style="fill:#ffffff;fill-opacity:1;stroke-width:0.182031" id="path846" />
                        <path
                            d="M 1.5581546,0.94474048 2.6457566,2.0324189 3.7334348,0.94474048 4.3469265,1.5581547 3.2592475,2.6458334 4.3469265,3.7334353 3.7334348,4.3469261 2.6457566,3.2593243 1.5581546,4.3469261 0.9447402,3.7334353 2.0323422,2.6458334 0.9447402,1.5581547 Z"
                            style="fill:#f46464;fill-opacity:1;stroke:none;stroke-width:0.0512157" id="path2740-3" />
                    </g>
                </svg>
            </a>
            <div :id="popup_content_id" class="text-center"></div>
        </div>

        <!--div :id="popup_id" class="ol-popup">
            <a href="#" :id="popup_closer_id" class="ol-popup-closer">
                <svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='20' width='20' class="close-icon">
                    <g transform='scale(3)'>
                        <path d     ="M 5.2916667,2.6458333 A 2.6458333,2.6458333 0 0 1 2.6458335,5.2916667 2.6458333,2.6458333 0 0 1 0,2.6458333 2.6458333,2.6458333 0 0 1 2.6458335,0 2.6458333,2.6458333 0 0 1 5.2916667,2.6458333 Z" style="fill:#ffffff;fill-opacity:1;stroke-width:0.182031" id="path846" />
                        <path d     ="M 1.5581546,0.94474048 2.6457566,2.0324189 3.7334348,0.94474048 4.3469265,1.5581547 3.2592475,2.6458334 4.3469265,3.7334353 3.7334348,4.3469261 2.6457566,3.2593243 1.5581546,4.3469261 0.9447402,3.7334353 2.0323422,2.6458334 0.9447402,1.5581547 Z" style="fill:#f46464;fill-opacity:1;stroke:none;stroke-width:0.0512157" id="path2740-3" />
                    </g>
                </svg>
            </a>
            <div :id="popup_content_id"></div>
        </div-->
        <div class="row shapefile-row">
            <div class="col-sm-6 border p-2">
                <div class="row mb-2">
                    <div class="col"><label for="shapefile_document" class="fw-bold">Upload Shapefile </label></div>
                    <div class="col">
                        <FileField :readonly="false" ref="shapefile_document" name="shapefile_document"
                            id="shapefile_document_document" :isRepeatable="true" :documentActionUrl="shapefileDocumentUrl"
                            :replace_button_by_text="true" fileTypes=".dbf, .prj, .shp, .shx" text_string="Attach File (.prj .dbf .shp
                            .shx)" />
                    </div>
                </div>
                <div class="row">
                    <div class="col">
                        <BootstrapAlert>If you do not upload a .prj file, we will use <a
                                href="https://en.wikipedia.org/wiki/World_Geodetic_System#WGS84" target="_blank">WGS 84</a>
                            / 'EPSG:4326'
                        </BootstrapAlert>
                    </div>

                </div>
                <div class="row">
                    <div class="col">
                        <button type="button" v-if="is_validating" disabled class="btn btn-primary">
                            <div class="row">
                                <div class="col-sm-12 text-nowrap text-truncate"><i class="fa fa-spinner fa-spin"></i>
                                </div>
                            </div>
                        </button>
                        <button type="button" v-else class="btn btn-primary" @click="validate_map_docs">
                            <div class="row">
                                <div class="col-sm-12 text-nowrap text-truncate">Process Files</div>
                            </div>
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-sm-6">
                <div id="legend_title"></div>
                <div id="legend">
                    <img src="" />
                </div>
            </div>
        </div>
        <VueAlert v-if="errorString && errorString.length" type="danger" style="color: red"><strong>{{ errorString
        }}</strong></VueAlert>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import Feature from 'ol/Feature';
import WMTSCapabilities from 'ol/format/WMTSCapabilities';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import TileWMS from 'ol/source/TileWMS';
import WMTS, { optionsFromCapabilities } from 'ol/source/WMTS';
import GeoJSON from 'ol/format/GeoJSON';
import Overlay from 'ol/Overlay';
import { FullScreen, MousePosition, defaults as olDefaults, OverviewMap, ScaleLine, ZoomSlider, ZoomToExtent } from 'ol/control';
import { Draw, Modify, Snap, Select } from 'ol/interaction';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import MeasureStyles, { formatLength } from '@/components/common/measure.js'
import { LineString, Point, Polygon } from 'ol/geom';
import { Circle as CircleStyle, Fill, Stroke, Style, Text, RegularShape } from 'ol/style';
import FileField from '@/components/forms/filefield_immediate.vue'
import VueAlert from '@vue-utils/alert.vue'
import { api_endpoints, helpers } from '@/utils/hooks'
import RangeSlider from '@/components/forms/range_slider.vue'
//import { getDisplayNameFromStatus, getDisplayNameOfCategory, getStatusForColour, getApiaryFeatureStyle } from '@/components/common/site_colours.js'
import { addOptionalLayers, set_mode, baselayer_name, polygon_style } from '@/components/common/map_functions.js'
import Swal from 'sweetalert2'

export default {
    name: 'ComponentMap',
    emits: ['refreshFromResponse'],
    props: {
        proposal: {
            type: Object,
            required: false,
        },
        competitive_process: {
            type: Object,
            require: false,
        },
        readonly: {
            type: Boolean,
            default: true,
        },
    },
    data: function () {
        return {
            showSatIcon: true,
            map: null,
            elem_id: uuid(),
            popup_id: uuid(),
            popup_closer_id: uuid(),
            popup_content_id: uuid(),
            overlay: null,
            content_element: null,
            modifyInProgressList: [],
            tileLayerMapbox: null,
            tileLayerSat: null,
            optionalLayers: [],
            hover: false,
            mode: 'normal',
            drawForMeasure: null,
            drawForLeaselicence: null,
            style: MeasureStyles.defaultStyle,
            segmentStyle: MeasureStyles.segmentStyle,
            labelStyle: MeasureStyles.labelStyle,
            segmentStyles: null,
            //leaselicenceQuerySource: null,
            leaselicenceQuerySource: new VectorSource({}),
            leaselicenseQueryLayer: null,
            selectedFeatureId: null,
            newFeatureId: 1,
            errorString: '',
            set_mode: set_mode,
            is_validating: false,
            lastPoint: null,
            sketchCoordinates: [[]],
            sketchCoordinatesHistory: [[]],
        }
    },

    components: {
        FileField,
        VueAlert,
        RangeSlider,
    },
    computed: {
        shapefileDocumentUrl: function () {
            let endpoint = ''
            let obj_id = 0
            if (this.proposal) {
                endpoint = api_endpoints.proposal
                obj_id = this.proposal.id
            } else if (this.competitive_process) {
                endpoint = api_endpoints.competitive_process
                obj_id = this.competitive_process.id
            } else {
                return ''  // Should not reach here.  Either this.proposal or this.competitive process should have an object.
            }
            let url = helpers.add_endpoint_join(
                // api_endpoints.proposal,
                endpoint, '/' + obj_id + '/process_shapefile_document/'
            )
            console.log({ url })
            return url
        },
        valid_button_disabled: function () {
            return false;
            /*
            if(this.is_external && this.proposal && !this.proposal.readonly){
                return false;
            }
            return true;
            */
        },
        showUndoButton: function () {
            return this.mode == 'draw' &&
                this.drawForLeaselicence &&
                this.drawForLeaselicence.getActive() &&
                this.sketchCoordinates.length > 1
        },
        showRedoButton: function () {
            return false;
            // Todo: The redo button is partially implemented so it is disabled for now.
            return this.mode == 'draw' &&
                this.drawForLeaselicence &&
                this.drawForLeaselicence.getActive() &&
                this.sketchCoordinatesHistory.length > this.sketchCoordinates.length
        },
    },
    methods: {
        valueChanged: function (value, tileLayer) {
            //tileLayer.setOpacity((100 - value)/100)
            tileLayer.setOpacity(value / 100)
        },
        /**
         * Adds uploaded shapefiles as layers to the map
         */
        updateShape: function () {
            let vm = this
            vm.shapeVectorSource = null;
            vm.shapeVectorLayer = null;
            // Polygon styling
            let fill = new Fill({
                color: 'rgba(255, 255, 255, 0.66)',
            })
            let style_valid = new Style({
                fill: fill,
                stroke: new Stroke({
                    color: 'white',
                }),
            })
            let style_inv = new Style({
                fill: fill,
                stroke: new Stroke({
                    color: 'red',
                }),
            })

            if (vm.shapefile_json && Object.keys(vm.shapefile_json).length > 0) {
                // console.log(vm.shapefile_json);

                let invalid_files = []
                // Add polygons uploaded by the user that already have been added as layer to a list
                let added_layer = []
                vm.map.getLayers().getArray()
                    .filter(layer => typeof (layer.get('source_')) !== 'undefined')
                    .forEach(layer => added_layer.push(layer));

                // Remove all layer where the respective previously uploaded file has been removed
                if (added_layer.length > vm.shapefile_json["features"].length) {
                    let shapefile_sources = []
                    vm.shapefile_json["features"].forEach(json => {
                        shapefile_sources.push(json["properties"]["source_"])
                    });

                    added_layer.forEach(layer => {
                        if (!shapefile_sources.includes(layer.get('source_'))) {
                            console.log(`Layer ${layer.get('source_')} seems to have been removed`)
                            vm.map.removeLayer(layer)
                        };
                    });
                }

                // Iterate over every feature in the feature collection from the shapefiles
                for (let i in vm.shapefile_json["features"]) {
                    let feature = vm.shapefile_json["features"][i];

                    // Check whether the feature has already been added to the map
                    let _found = false;
                    let source_ = feature["properties"]["source_"]
                    added_layer.every(layer => {
                        if (layer.get('source_') === source_) {
                            _found = true;
                            return false;
                        }
                        return true;
                    });

                    // Add feature as layer if not yet present
                    if (!_found) {
                        let shapeVectorSource = new VectorSource({
                            features: new GeoJSON().readFeatures(feature),
                        });
                        let shapeVectorLayer = new VectorLayer({
                            source: shapeVectorSource,
                            style: function (feature, resolution) {
                                const name = feature.get('valid');
                                return name == true ? style_valid : style_inv;
                            },
                        })
                        shapeVectorLayer.set('source_', source_);
                        vm.map.addLayer(shapeVectorLayer);
                    } else {
                        console.log(`Layer ${source_} already exists`);
                    }

                    // Check whether there is an invalid feature polygon (e.g. does not intersect with DBCA geometries)
                    if (feature["properties"]['valid'] == false) {
                        invalid_files.push(source_)
                    };
                }
                swal.fire({
                    title: "Validation",
                    text: invalid_files.length == 0 ? 'Polygons are valid' : `${invalid_files.join(', ')} are not valid`,
                    icon: invalid_files.length == 0 ? 'success' : 'warning'
                })

                vm.displayAllFeatures() //.displayAllFeaturesShape();
            }
        },
        validate_map_docs: function () {
            let vm = this;
            vm.is_validating = true;
            vm.errorString = '';
            let endpoint = api_endpoints.proposals
            const options = {
                'method': 'POST',
                'content-type': 'application/json'
            };
            // fetch(helpers.add_endpoint_json(endpoint,vm.proposal.id+'/validate_map_files'), options).then(response => response.json())
            // .then(data => {
            fetch(helpers.add_endpoint_json(api_endpoints.proposals, vm.proposal.id + '/validate_map_files'), options).then(async response => {
                if (!response.ok) {
                    const text = await response.json();
                    throw new Error(text);
                } else {
                    return response.json();
                }
            })
                .then(data => {
                    vm.$emit('refreshFromResponse', data);
                    vm.$nextTick(() => {
                        vm.loadLeaseLicenceGeometry();
                        vm.fitToLayer();
                        Swal.fire(
                            'Success',
                            'Shapefile processed successfully',
                            'success'
                        )
                    });
                    // vm.shapefile_json = data.shapefile_json;
                    // vm.updateShape();
                    vm.is_validating = false;
                })
                .catch(error => {
                    console.log(error);
                    vm.errorString = helpers.apiVueResourceError(error);
                    vm.is_validating = false;
                    swal.fire({
                        title: "Validation",
                        text: error,
                        icon: 'error'
                    })
                });
        },

        loadLeaseLicenceGeometry: function () {
            const nonIntersectingStyle = new Style({
                fill: new Fill({
                    color: '#ff0000',
                }),
                stroke: new Stroke({
                    color: 'rgba(255, 255, 255, 0.7)',
                    width: 2,
                }),
            });

            let geometries = { "type": "FeatureCollection", "features": [] }
            if (this.proposal && this.proposal.proposalgeometry) {
                geometries = this.proposal.proposalgeometry
                Object.keys(geometries["features"]).forEach(function (key, _) {
                    geometries["features"][key]["properties"]["source"] = "registration_of_interest";
                });
            } else if (this.competitive_process && this.competitive_process.competitive_process_geometries) {
                let proposalgeometries = null;
                geometries = this.competitive_process.competitive_process_geometries
                Object.keys(geometries["features"]).forEach(function (key, _) {
                    geometries["features"][key]["properties"]["source"] = "competitive_process";
                });
                // Append proposal geometries to competitive process geometries
                if (this.competitive_process.registration_of_interest) {
                    proposalgeometries = this.competitive_process.registration_of_interest.proposalgeometry;
                    Object.keys(proposalgeometries["features"]).forEach(function (key, _) {
                        proposalgeometries["features"][key]["properties"]["source"] = "registration_of_interest";
                    });
                    for (let feature of proposalgeometries["features"]) {
                        geometries["features"].push(feature);
                    }
                }
            }
            if (geometries) {
                for (let poly of geometries.features) {
                    const feature = (new GeoJSON).readFeature(poly);
                    //console.log(feature)
                    if (!feature.getProperties().intersects) {
                        feature.setStyle(nonIntersectingStyle);
                    } else {
                        // feature.setStyle(new Style({
                        //     fill: new Fill({
                        //         color: '#fff',
                        //     }),
                        //     stroke: new Stroke({
                        //         color: 'rgba(255, 255, 255, 0.7)',
                        //         width: 2,
                        //     }),
                        // }))
                    }
                    feature.setProperties({ "id": this.newFeatureId });
                    this.leaselicenceQuerySource.addFeature(feature);
                    this.newFeatureId++;
                };
            }
            this.forceToRefreshMap();
        },

        getJSONFeatures: function () {
            //const format = new GeoJSON({featureProjection: 4326});
            const format = new GeoJSON();
            const features = this.leaselicenceQuerySource.getFeatures();
            /*
            console.log(format.writeFeatures(features));
            console.log(this.leaselicenceQuerySource.getFeatures())
            */
            return format.writeFeatures(features);
        },
        toggleSatIcon: function (layer) {
            if (layer === 'osm') {
                this.showSatIcon = true;
            } else {
                this.showSatIcon = false;
            }
        },
        fitToLayer: function () {
            const extent = this.leaselicenceQuerySource.getExtent();
            if (!(extent[0] === Infinity)) {
                this.map.getView().fit(this.leaselicenceQuerySource.getExtent());
            }
            this.unlistenFitToLayer();
        },
        unlistenFitToLayer: function () {
            this.map.un('rendercomplete', this.fitToLayer);
        },
        initMap: async function () {
            let vm = this;
            // Full screen toggle
            const fullScreenControl = new FullScreen();
            // Show mouse coordinates
            const mousePositionControl = new MousePosition({
                coordinateFormat: function (coords) {
                    let message = vm.getDegrees(coords) + "\n";
                    return message;
                },
                target: document.getElementById('mouse-position'),
                className: 'custom-mouse-position',
            });
            /*
            const scaleLineControl = new ScaleLine();
            const zoomSliderControl = new ZoomSlider();
            const zoomToExtentControl = new ZoomToExtent({
                extent: [112, -29, 119, -34],
                });
                */

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
            });
            vm.tileLayerSat = new TileLayer({
                title: 'Satellite',
                type: 'base',
                visible: false,
                source: satelliteTileWms,
            })

            vm.map = new Map({
                controls: olDefaults().extend([
                    fullScreenControl,
                    mousePositionControl,
                    /*
                    zoomSliderControl,
                    zoomToExtentControl,
                    overviewMapControl,
                    scaleLineControl,
                    */
                ]),
                layers: [
                    vm.tileLayerMapbox,
                    vm.tileLayerSat,
                ],
                target: vm.elem_id,
                view: new View({
                    center: [115.95, -31.95],
                    zoom: 7,
                    projection: 'EPSG:4326',
                    /*
                    maxZoom: 12,
                    minZoom: 3,
                    */
                })
            });

            vm.drawForLeaselicence = new Draw({
                source: vm.leaselicenceQuerySource,
                //type: 'MultiPolygon',
                type: 'Polygon',
                //style: vm.styleFunctionForMeasurement,
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
            })
            vm.drawForLeaselicence.on('drawstart', function (evt) {
                vm.lastPoint = null;
            });
            vm.drawForLeaselicence.on('click'), function (evt) {
                console.log(evt);
            }
            vm.drawForLeaselicence.on('drawend', function (evt) {
                console.log(evt);
                console.log(evt.feature.values_.geometry.flatCoordinates);
                //evt.feature.setId(vm.newFeatureId)
                evt.feature.setProperties({ "id": vm.newFeatureId })
                vm.newFeatureId++;
                console.log('newFeatureId = ' + vm.newFeatureId);
                vm.lastPoint = evt.feature;
                vm.sketchCoordinates = [[]];
                vm.sketchCoordinatesHistory = [[]];

            });
            vm.leaselicenceQueryLayer = new VectorLayer({
                title: "Application Area of Interest",
                source: vm.leaselicenceQuerySource,
                style: polygon_style,
            });
            //console.log(vm.drawForLeaselicence);
            vm.map.addInteraction(vm.drawForLeaselicence);
            vm.map.addLayer(vm.leaselicenceQueryLayer);
            // update map extent when new features added
            vm.map.on('rendercomplete', vm.fitToLayer);

            // Set zIndex to some layers to be rendered over the other layers
            vm.leaselicenceQueryLayer.setZIndex(10);


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
                //vm.drawForMeasure.finishDrawing()
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

            let container = document.getElementById(vm.popup_id)
            vm.content_element = document.getElementById(vm.popup_content_id)
            let closer = document.getElementById(vm.popup_closer_id)

            vm.overlay = new Overlay({
                element: container,
                autoPan: false,
                offest: [0, -10]
            })

            closer.onclick = function () {
                vm.closePopup()
                closer.blur()
                return false
            }

            vm.map.addOverlay(vm.overlay)

            // select and delete polygons
            const selected = new Style({
                fill: new Fill({
                    color: '#eeeeee',
                }),
                stroke: new Stroke({
                    color: 'rgba(255, 255, 255, 0.7)',
                    width: 2,
                }),
            });

            function selectStyle(feature) {
                const color = feature.get('COLOR') || '#eeeeee';
                selected.getFill().setColor(color);
                return selected;
            }

            // select interaction working on "singleclick"
            const selectSingleClick = new Select({
                style: selectStyle,
                layers: [vm.leaselicenceQueryLayer,],
            });
            vm.map.addInteraction(selectSingleClick);
            selectSingleClick.on('select', (e) => {
                if (e.selected && e.selected.length > 0) {
                    //vm.selectedFeatureId = e.selected[0].getId();
                    vm.selectedFeatureId = e.selected[0].getProperties().id;
                } else {
                    vm.selectedFeatureId = null;
                }
            });
            vm.map.on('singleclick', function (evt) {
                if (vm.mode === 'layer') {
                    vm.closePopup()
                    let view = vm.map.getView()
                    let viewResolution = view.getResolution()

                    // Add click event popup to drawn polygons
                    vm.map.forEachFeatureAtPixel(evt.pixel,
                        (feature, layer) => {
                            let feature_format = new GeoJSON();
                            let geojson_str = feature_format.writeFeature(
                                feature,
                                { dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857' });
                            if (geojson_str.length > 0) {
                                let geojson = { "type": "FeatureCollection", "features": [] }
                                geojson["features"].push(JSON.parse(geojson_str));
                                vm.showPopupForLayersJson(
                                    geojson,
                                    evt.coordinate,
                                    ["source"],
                                    true,
                                    vm.leaselicenceQueryLayer);
                            }
                        }
                    )

                    // Retrieve active layers' sources
                    for (let i = 0; i < vm.optionalLayers.length; i++) {
                        let visibility = vm.optionalLayers[i].getVisible()
                        if (visibility) {
                            // Retrieve column names to be displayed
                            let column_names = vm.optionalLayers[i].get('columns')
                            column_names = column_names.map(function (col) {
                                // Convert array of dictionaries to simple array
                                if (vm.is_internal && col.option_for_internal) {
                                    return col.name
                                }
                                if (vm.is_external && col.option_for_external) {
                                    return col.name
                                }
                            })
                            // Retrieve the value of display_all_columns boolean flag
                            let display_all_columns = vm.optionalLayers[i].get('display_all_columns')

                            // Retrieve the URL to query the attributes
                            let source = vm.optionalLayers[i].getSource()
                            let url = source.getFeatureInfoUrl(
                                evt.coordinate, viewResolution, view.getProjection(),
                                //{'INFO_FORMAT': 'text/html'}
                                { 'INFO_FORMAT': 'application/json' }
                            )

                            fetch(url).then(async response => {
                                if (!response.ok) {
                                    return await response.json().then(json => { throw new Error(json); });
                                } else {
                                    return await response.json();
                                }
                            })
                                .then(data => {
                                    if (data.features.length > 0) {
                                        console.log(data);
                                        vm.showPopupForLayersJson(data, evt.coordinate, column_names, display_all_columns, vm.optionalLayers[i]);
                                    }
                                })
                                .catch(error => {
                                    console.log(error);
                                })

                            /*
                            // Query
                            let p = fetch(url, {
                                credentials: 'include'
                            })

                            //p.then(res => res.text()).then(function(data){
                            p.then(res => res.json()).then(function(data){
                                //vm.showPopupForLayersHTML(data, evt.coordinate, column_names, display_all_columns)
                                vm.showPopupForLayersJson(data, evt.coordinate, column_names, display_all_columns, vm.optionalLayers[i])
                            })
                            */
                        }
                    }
                }
            });
        },
        undoLeaseLicensePoint: function () {
            let vm = this;
            console.log(vm.drawForLeaselicence.sketchCoords_)
            if (vm.lastPoint) {
                vm.leaselicenceQuerySource.removeFeature(vm.lastPoint);
                vm.lastPoint = null;
                vm.sketchCoordinates = [[]]
                vm.sketchCoordinatesHistory = [[]]
                this.selectedFeatureId = null;
            } else {
                vm.drawForLeaselicence.removeLastPoint();
            }
        },
        redoLeaseLicensePoint: function () {
            let vm = this;
            if (vm.sketchCoordinatesHistory.length > vm.sketchCoordinates.length) {
                let nextCoordinate = vm.sketchCoordinatesHistory.slice(vm.sketchCoordinates.length, vm.sketchCoordinates.length + 1);
                vm.drawForLeaselicence.appendCoordinates([nextCoordinate[0]]);
            }
        },
        removeLeaselicenceFeature: function () {
            //const feature = this.leaselicenceQuerySource.getFeatureById(this.selectedFeatureId);
            const feature = this.leaselicenceQuerySource.forEachFeature((feat) => {
                if (feat.getProperties().id === this.selectedFeatureId) {
                    return feat;
                }
                console.log(feat.getProperties())
            });
            console.log(feature)
            this.leaselicenceQuerySource.removeFeature(feature);
            this.selectedFeatureId = null;
        },
        /*
        showPopupById: function(apiary_site_id){
            let feature = this.apiarySitesQuerySource.getFeatureById(apiary_site_id)
            this.showPopup(feature)
        },
        */
        showPopup: function (feature) {
            console.log("showPopup");
            if (feature) {
                let geometry = feature.getGeometry();
                let coord = geometry.getCoordinates();
                let svg_hexa = "<svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='20' width='15'>" +
                    '<g transform="translate(0, 4) scale(0.9)"><path d="M 14.3395,12.64426 7.5609998,16.557828 0.78249996,12.64426 0.7825,4.8171222 7.5609999,0.90355349 14.3395,4.8171223 Z" id="path837" style="fill:none;stroke:#ffffff;stroke-width:1.565;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" /></g></svg>'
                //let status_str = feature.get('is_vacant') ? getDisplayNameFromStatus(feature.get('status')) + ' (vacant)' : getDisplayNameFromStatus(feature.get('status'))
                let status_str = getDisplayNameFromStatus(getStatusForColour(feature, false, this.display_at_time_of_submitted))
                let content = '<div style="padding: 0.25em;">' +
                    '<div style="background: darkgray; color: white; text-align: center;" class="align-middle">' + svg_hexa + ' site: ' + feature.id_ + '</div>' +
                    '<div style="font-size: 0.8em;">' +
                    '<div>' + status_str + '</div>' +
                    '<div>' + getDisplayNameOfCategory(feature.get('site_category')) + '</div>' +
                    '<div>' + feature['values_']['geometry']['flatCoordinates'] + '</div>' +
                    '</div>' +
                    '</div>'
                this.content_element.innerHTML = content;
                this.overlay.setPosition(coord);
            }
        },
        showPopupForLayersJson: function (geojson, coord, column_names, display_all_columns, target_layer) {
            console.log("popup opt layers")
            let wrapper = $('<div>')  // Add wrapper element because html() used at the end exports only the contents of the jquery object
            let caption = $('<div style="text-align:center; font-weight: bold;">').text(target_layer.get('title'))
            let table = $('<table style="margin-bottom: 1em;">') //.addClass('table')
            let tbody = $('<tbody>')
            let outer = $('<div style="overflow-y:scroll; overflow-x:auto; max-height:300px; max-width:600px;">')
            wrapper.append(caption)
            wrapper.append(table.append(tbody))

            for (let feature of geojson.features) {
                for (let key in feature.properties) {
                    if (display_all_columns || column_names.includes(key)) {
                        let tr = $('<tr style="border-bottom:1px solid lightgray;">')
                        let th = $('<th style="padding:0 0.5em;">').text(key)
                        let td = $('<td>').addClass('text-nowrap').text(feature.properties[key])
                        tr.append(th)
                        tr.append(td)
                        tbody.append(tr)
                    }
                }
            }
            outer = $('<div>').wrapInner(outer.wrapInner(wrapper.html()))
            this.content_element.innerHTML += outer.html() //wrapper.html()  // Export contents as HTML string
            this.overlay.setPosition(coord);
        },
        showPopupForLayersHTML: function (html_str, coord, column_names, display_all_columns) {
            // Generate jquery object from html_str
            let html_obj = $('<div>').html(html_str)

            // Retrieve tables as jquery object
            let tables = html_obj.find("table")

            if (!display_all_columns) {
                // Hide all columns
                tables.find('th,td').css('display', 'none')

                // Make a certain column visible
                for (let i = 0; i < column_names.length; i++) {
                    let index = tables.find('th').filter(function () {
                        // <th> element whoose text is exactly same as column_names[i]
                        return $(this).text() === column_names[i]
                    }).css('display', '').index()

                    let idx = index + 1

                    // Display <td> in the same column
                    let td = tables.find('td:nth-child(' + idx + ')')
                    td.css('display', '')
                }
            }

            if (tables.length) {
                this.content_element.innerHTML += html_obj.html()
                this.overlay.setPosition(coord);
            }
        },

        closePopup: function () {
            this.content_element.innerHTML = null
            this.overlay.setPosition(undefined)
            this.$emit('popupClosed')
        },
        displayAllFeatures: function () {
            if (this.map) {
                if (this.leaselicenceQuerySource.getFeatures().length > 0) {
                    let view = this.map.getView()

                    let ext = this.leaselicenceQuerySource.getExtent()
                    let centre = [(ext[0] + ext[2]) / 2.0, (ext[1] + ext[3]) / 2.0]
                    let resolution = view.getResolutionForExtent(ext);
                    let z = view.getZoomForResolution(resolution) - 1
                    view.animate({ zoom: z, center: centre })
                }
            }
        },
        addJoint: function (point, styles) {
            let s = new Style({
                image: new CircleStyle({
                    radius: 2,
                    fill: new Fill({
                        color: '#3399cc'
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
        forceToRefreshMap: function () {
            let vm = this
            setTimeout(function () {
                vm.map.updateSize();
            }, 700)
            // console.log(document.getElementById(this.elem_id))
        },
        setBaseLayer: function (selected_layer_name) {
            console.log('in setBaseLayer')
            if (selected_layer_name == 'sat') {
                this.toggleSatIcon('sat');
                this.tileLayerMapbox.setVisible(false)
                this.tileLayerSat.setVisible(true)
            } else {
                this.toggleSatIcon('osm');
                this.tileLayerMapbox.setVisible(true)
                this.tileLayerSat.setVisible(false)
            }
        },
        getDegrees: function (coords) {
            return coords[0].toFixed(6) + ', ' + coords[1].toFixed(6);
        },
        clearMeasurementLayer: function () {
            let vm = this
            let features = vm.measurementLayer.getSource().getFeatures()
            features.forEach((feature) => {
                vm.measurementLayer.getSource().removeFeature(feature)
            })
        },
        changeLayerVisibility: function (targetLayer) {
            if (!targetLayer.getVisible()) {
                // add
                targetLayer.setVisible(true);
                sessionStorage.setItem('optionalLayer_' + targetLayer.getProperties().id, true);
            } else {
                // remove
                targetLayer.setVisible(false);
                sessionStorage.removeItem('optionalLayer_' + targetLayer.getProperties().id);
            }
        },
    },
    created() {
        /*
        this.$nextTick(() => {
            this.loadLeaseLicenceGeometry();
            //this.displayAllFeatures();
        });
        */
    },
    mounted() {
        this.initMap();
        //vm.setBaseLayer('osm')
        set_mode.bind(this)('layer')
        addOptionalLayers(this)
        this.$nextTick(() => {
            this.loadLeaseLicenceGeometry();
        });
    },
}
</script>

<style lang="css" scoped>
@import '../../../../../static/leaseslicensing/css/map.css';


.shapefile-row {
    margin-left: 1px;
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
</style>
