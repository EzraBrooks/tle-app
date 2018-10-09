window.addEventListener('load', function () {
    var viewer = new Cesium.Viewer(document.getElementById('cesium-container'));
    viewer.dataSources.add(Cesium.CzmlDataSource.load('/orbits'));
})