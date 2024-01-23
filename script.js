async function updateMap() {
    const response = await fetch('/weather_data');
    const data = await response.json();

    // Use the processed data to update the map
    console.log(data);

    const map = L.map('map').setView([data.map_data.lat, data.map_data.lon], 10);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    L.marker([data.map_data.lat, data.map_data.lon]).addTo(map)
        .bindPopup(`Temperature: ${data.map_data.temp}°C, Humidity: ${data.map_data.humidity}%`);

    // Create a heatmap layer
    const heatmapLayer = L.heatLayer([[data.map_data.lat, data.map_data.lon, 1]]).addTo(map);

    // Add data points to the heatmap layer
    heatmapLayer.addLatLng([data.map_data.lat, data.map_data.lon, 1]);

    // Display VPD and aridity index
    document.getElementById("vpd").innerText = `VPD: ${data.vpd} hPa`;
    document.getElementById("aridity_index").innerText = `Aridity Index: ${data.aridity_index}`;
}

window.onload = updateMap;
