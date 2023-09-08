import WMSCapabilities from 'ol/format/WMSCapabilities';
import TileWMS from 'ol/source/TileWMS';
import TileLayer from 'ol/layer/Tile';
import { Style, Fill, Stroke } from 'ol/style';

// Tile server url
// eslint-disable-next-line no-undef
var url = `${env['kmi_server_url']}/geoserver/public/wms/?SERVICE=WMS&VERSION=1.0.0&REQUEST=GetCapabilities`;
// Layer to use as map base layer
export var baselayer_name = 'mapbox-emerald';
// export var baselayer_name = 'mapbox-dark'

/**
 * Queries the WMS server for its capabilities and adds optional layers to a map
 * @param {Proxy} map_component A map component instance
 */
export function addOptionalLayers(map_component) {
    let parser = new WMSCapabilities();

    fetch(url)
        .then(function (response) {
            return response.text();
        })
        .then(function (text) {
            let result = parser.read(text);
            let layers = result.Capability.Layer.Layer.filter((layer) => {
                return layer['Name'] === 'dbca_legislated_lands_and_waters';
            });

            for (let j in layers) {
                let layer = layers[j];

                let l = new TileWMS({
                    // eslint-disable-next-line no-undef
                    url: `${env['kmi_server_url']}/geoserver/public/wms`,
                    params: {
                        FORMAT: 'image/png',
                        VERSION: '1.1.1',
                        tiled: true,
                        STYLES: '',
                        LAYERS: `public:${layer.Name}`,
                    },
                });

                let tileLayer = new TileLayer({
                    name: layer.Name,
                    abstract: layer.Abstract.trim(),
                    title: layer.Title.trim(),
                    visible: false,
                    source: l,
                });

                let legend_url = null;
                if (layer.Name == baselayer_name) {
                    // TODO don't add the baselayer to the optional layer control
                } else {
                    if (typeof layer.Style != 'undefined') {
                        legend_url = layer.Style[0].LegendURL[0].OnlineResource;
                    }
                }

                // Set additional attributes to the layer
                tileLayer.set('columns', []); // []
                tileLayer.set('display_all_columns', true); // true
                tileLayer.set('legend_url', legend_url);

                map_component.optionalLayers.push(tileLayer);
                map_component.map.addLayer(tileLayer);

                tileLayer.on('change:visible', function (e) {
                    if (e.oldValue == false) {
                        $('#legend')
                            .find('img')
                            .attr('src', this.values_.legend_url);
                        $('#legend_title').text(this.values_.title);
                    } else if (e.oldValue == true) {
                        $('#legend_title').text('');
                        $('#legend').find('img').attr('src', '');
                        // Hide any overlays when the optional layer is turned off
                        map_component.overlay(undefined);
                    } else {
                        console.error(
                            'Cannot assess tile layer visibility change.'
                        );
                    }
                });

                // Lets ol display a popup with clicked feature properties
                map_component.map.on('singleclick', function (evt) {
                    if (map_component.mode !== 'info') {
                        return;
                    }
                    let coordinate = evt.coordinate;
                    map_component.map.forEachLayerAtPixel(
                        evt.pixel,
                        function (lay) {
                            if (lay.values_.name === tileLayer.values_.name) {
                                console.log('Clicked on tile layer', lay);

                                let point = `POINT (${coordinate.join(' ')})`;
                                let query_str = _helper.geoserverQuery.bind(
                                    this
                                )(point, map_component);
                                map_component
                                    .validateFeatureQuery(query_str)
                                    .then(async (features) => {
                                        if (features.length === 0) {
                                            console.warn(
                                                'No features found at this location.'
                                            );
                                            map_component.overlay(undefined);
                                        } else {
                                            console.log('Feature', features);
                                            map_component.overlay(
                                                coordinate,
                                                features[0]
                                            );
                                        }
                                        map_component.errorMessageProperty(
                                            null
                                        );
                                    });
                            }
                        }
                    );
                });
            }
        });
}

/**
 * Sets the mode of interaction of the map.
 * @param {string} mode The mode to set the map to (layer, draw, measure)
 */
export function set_mode(mode) {
    // Toggle map mode on/off when the new mode is the old one
    if (this.mode == mode) {
        this.mode = 'layer';
    } else {
        this.mode = mode;
    }

    this.drawing = false;
    this.measuring = false;
    this.informing = false;
    this.errorMessageProperty(null);
    this.overlay(undefined);
    this.map.getTargetElement().style.cursor = 'default';

    if (this.mode === 'layer') {
        this.clearMeasurementLayer();
        _helper.toggle_draw_measure_license.bind(this)(false, false);
    } else if (this.mode === 'draw') {
        this.clearMeasurementLayer();
        this.sketchCoordinates = [[]];
        this.sketchCoordinatesHistory = [[]];
        _helper.toggle_draw_measure_license.bind(this)(false, true);
        this.drawing = true;
    } else if (this.mode === 'measure') {
        _helper.toggle_draw_measure_license.bind(this)(true, false);
        this.measuring = true;
    } else if (this.mode === 'info') {
        _helper.toggle_draw_measure_license.bind(this)(false, false);
        this.informing = true;
    } else {
        console.error(`Cannot set mode ${mode}`);
        return false;
    }
    // Call back to the map so selected features can adept their style to the new mode
    this.select.dispatchEvent({
        type: 'map:modeChanged',
        details: {
            new_mode: this.mode,
        },
    });

    return true;
}

/**
 * Defines polygon feature styling depending on whether the polygon source
 * is a Registration of Interest or a Competitive Process
 * @param {object} feature A single geometry feature (e.g. a drawn polygon)
 */
export function polygon_style(feature) {
    let strokecolor = '#3498DB';
    let fillcolor = '#85C1E9';
    if (feature.get('source') === 'registration_of_interest') {
        // yellowish
        strokecolor = [244, 208, 63, 1.0];
        fillcolor = [241, 196, 15, 0.7];
    } else if (feature.get('source') === 'competitive_process') {
        // orangish
        strokecolor = [240, 178, 122, 1.0];
        fillcolor = [230, 126, 34, 0.7];
    }
    return new Style({
        fill: new Fill({
            color: fillcolor,
        }),
        stroke: new Stroke({
            color: strokecolor,
            width: 1,
        }),
    });
}

/**
 * Validate feature callback function. Calls `finnishDrawing` on the map component
 * when the feature is valid. A feature is condidered valid when it intersects with
 * the DBCS legislated land-water layer.
 */
export function validateFeature() {
    let vm = this;
    console.log('Validate feature');
    // Get the WKT representation of the drawn polygon
    let polygon_wkt = vm.$refs.component_map.featureToWKT();
    let query = _helper.geoserverQuery.bind(vm)(polygon_wkt);

    vm.$refs.component_map
        .validateFeatureQuery(query)
        .then(async (features) => {
            if (features.length === 0) {
                console.warn('New feature is not valid');
                vm.$refs.component_map.errorMessageProperty(
                    'The polygon you have drawn does not intersect with any DBCA lands or water.'
                );
            } else {
                console.log('New feature is valid', features);
                vm.$refs.component_map.finishDrawing();
            }
        });
}

export let owsQuery = {
    version: '1.0.0', // TODO: Change to 1.1.0 or 2.0.0 when supported by the geoserver
    landwater: {
        typeName: 'public:dbca_legislated_lands_and_waters',
        srsName: 'EPSG:4326',
        propertyName:
            'objectid,wkb_geometry,category,leg_act,leg_identifier,leg_name,leg_tenure,leg_vesting',
        geometry: 'wkb_geometry',
    },
};

/**
 * Module with map related helper functions
 */
const _helper = {
    /**
     * Toggles measure and polygon layer active or inactive
     * @param {boolean} drawForMeasure Whether to set the measure layer active or inactive
     * @param {boolean} drawForModel Whether to set the model's polygon layer active or inactive
     */
    toggle_draw_measure_license: function (drawForMeasure, drawForModel) {
        if (this.drawForMeasure) {
            this.drawForMeasure.setActive(drawForMeasure);
        }
        if (this.drawForModel) {
            this.drawForModel.setActive(drawForModel);
        }
    },
    /**
     * Builds a query string for the geoserver based on the provided WKT
     * @param {str} wkt A geometry in Well-known-text (WKT) format
     * @param {Object} map_component The map component
     * @returns A query string for the geoserver
     */
    geoserverQuery: function (wkt, map_component) {
        let vm = this;
        if (wkt === undefined) {
            console.warn('No WKT provided');
            return;
        }
        if (map_component === undefined) {
            map_component = vm.$refs.component_map;
        }
        // The geoserver url
        // eslint-disable-next-line no-undef
        let owsUrl = `${env['kmi_server_url']}/geoserver/public/ows/?`;
        // Create a params dict for the WFS request to the land-water layer
        let paramsDict = map_component.queryParamsDict('landwater');
        let geometry_name = map_component.owsQuery.landwater.geometry;
        paramsDict['CQL_FILTER'] = `INTERSECTS(${geometry_name},${wkt})`;

        // Turn params dict into a param query string
        let params = new URLSearchParams(paramsDict).toString();
        let query = `${owsUrl}${params}`;

        return query;
    },
};
