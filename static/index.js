// Might as well just leave this in the code since it's going to be blatantly available on the frontend anyway. pls no steal.
Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5ZTVkZTc3ZS0yODA4LTQwYmEtODhiMS0wOTgwYWI0YmM4YjkiLCJpZCI6Mzg0OSwic2NvcGVzIjpbImFzciIsImdjIl0sImlhdCI6MTUzOTA2MDMzOX0.U8fGq4kSS6zB9sIHYR8knd5Y07EbhjMiYu3aHucmtok';

window.addEventListener('load', function () {
    var viewer = new Cesium.Viewer(document.getElementById('cesium-container'));
    viewer.dataSources.add(Cesium.CzmlDataSource.load('/orbits'));
    viewer.clock.canAnimate = true;
    viewer.clock.shouldAnimate = true;
})