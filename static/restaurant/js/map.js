let vectorSource = new ol.source.Vector(),
    vectorLayer = new ol.layer.Vector({
        source: vectorSource
    }),
    styles = {
        route: new ol.style.Style({
            stroke: new ol.style.Stroke({
                width: 6, color: [40, 40, 40, 0.8]
            })
        }),
        icon: new ol.style.Style({
            image: new ol.style.Icon({
                anchor: [0.5, 1],
                src: icon_url
            })
        })
    };

let map = new ol.Map({
    target: 'map',
    layers: [
        new ol.layer.Tile({
            source: new ol.source.OSM()
        }),
        vectorLayer
    ],
    view: new ol.View({
        center: [8078795.833261827, 2632691.5825704993],
        zoom: 12
    })
});
map.on('click', function (evt) {
    let coord4326 = utils.to4326(evt.coordinate);
    utils.createFeature(coord4326);
    $("#id_long").val(coord4326[0].toString().slice(0, 9));
    $("#id_lat").val(coord4326[1].toString().slice(0, 9));
});

let utils = {
    createFeature: function (coord) {
        let feature = new ol.Feature({
            type: 'place',
            geometry: new ol.geom.Point(ol.proj.fromLonLat(coord))
        });
        feature.setStyle(styles.icon);
        vectorSource.clear();
        vectorSource.addFeature(feature);
    },
    to4326: function (coord) {
        return ol.proj.transform([
            parseFloat(coord[0]), parseFloat(coord[1])
        ], 'EPSG:3857', 'EPSG:4326');
    }
};