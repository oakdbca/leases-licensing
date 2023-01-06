import WMSCapabilities from 'ol/format/WMSCapabilities';
import TileWMS from 'ol/source/TileWMS';
import TileLayer from 'ol/layer/Tile';

// Tile server url
var url = `${env['kmi_server_url']}/geoserver/public/wms/?SERVICE=WMS&VERSION=1.0.0&REQUEST=GetCapabilities`;
// Layer to use as map base layer
export var baselayer_name = 'mapbox-emerald'
// export var baselayer_name = 'mapbox-dark'


/**
 * Queries the WMS server for its capabilities and adds optional layers to a map
 * @param {Proxy} map_component A map component instance
 */
export function addOptionalLayers(map_component) {
    let parser = new WMSCapabilities();

    fetch(url).then(function(response) {
        return response.text();
        }).then(function(text) {
            let result = parser.read(text);
            let layers = result.Capability.Layer.Layer.filter(layer => {return layer['Name'] === 'dbca_legislated_lands_and_waters'});

            for (let j in layers) {
                let layer = layers[j];

                let l = new TileWMS({
                    url: `${env['kmi_server_url']}/geoserver/public/wms`,
                    params: {
                        'FORMAT': 'image/png',
                        'VERSION': '1.1.1',
                        tiled: true,
                        STYLES: '',
                        LAYERS: `public:${layer.Name}`
                    }
                });

                let tileLayer= new TileLayer({
                    title: layer.Title.trim(),
                    visible: false,
                    source: l,
                })

                let legend_url = null;
                if (layer.Name == baselayer_name) {
                    // TODO don't add the baselayer to the optional layer control
                } else {
                    if (typeof(layer.Style) != 'undefined') {
                        legend_url = layer.Style[0].LegendURL[0].OnlineResource
                    }
                }

                // Set additional attributes to the layer
                tileLayer.set('columns', []) // []
                tileLayer.set('display_all_columns', true) // true
                tileLayer.set('legend_url', legend_url);

                map_component.optionalLayers.push(tileLayer)
                map_component.map.addLayer(tileLayer)

                tileLayer.on("change:visible", function(e){
                    if (e.oldValue == false) {
                        $('#legend').find('img').attr('src', this.values_.legend_url)
                        $('#legend_title').text(this.values_.title);
                    } else if (e.oldValue == true) {
                        $('#legend_title').text('');
                        $('#legend').find('img').attr('src', "")
                    } else {
                        console.error("Cannot assess tile layer visibility change.")
                    }
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
        this .mode = 'layer'
    } else {
        this .mode = mode
    }
    if (this .mode === 'layer'){
        this .clearMeasurementLayer()
        _helper.toggle_draw_measure_license.bind(this )(false, false)
    } else if (this .mode === 'draw') {
        this .clearMeasurementLayer()
        _helper.toggle_draw_measure_license.bind(this )(false, true)
    } else if (this .mode === 'measure') {
        _helper.toggle_draw_measure_license.bind(this )(true, false)
    } else {
        console.error(`Cannot set mode ${mode}`)
    }
}

/**
 * Module with map related helper functions
 */
const _helper =  {
    /**
     * Toggles measure and polygon layer active or inactive
     * @param {boolean} drawForMeasure Whether to set the measure layer active or inactive
     * @param {boolean} drawForLeaselicence Whether to set the polygon layer active or inactive
     */
    toggle_draw_measure_license: function(drawForMeasure, drawForLeaselicence) {
        if (this.drawForMeasure) {
            this.drawForMeasure.setActive(drawForMeasure)
        }
        if (this.drawForLeaselicence) {
            this.drawForLeaselicence.setActive(drawForLeaselicence)
        }
    }
}
