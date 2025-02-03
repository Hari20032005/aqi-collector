// Configuration
const CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bengaluru'];
const DATA_URL = 'https://cdn.jsdelivr.net/gh/Hari20032005/https://github.com/Hari20032005/aqi-collector/data/aqi_data.csv';

let aqiChart, pollutantsChart;
let allData = [];

async function loadData() {
    try {
        const response = await fetch(DATA_URL);
        const csvData = await response.text();
        
        allData = csvData.split('\n')
            .slice(1)
            .map(row => {
                const cols = row.split(',');
                return {
                    city: cols[0],
                    timestamp: luxon.DateTime.fromFormat(cols[1], 'yyyy-MM-dd HH:mm:ss'),
                    aqi: parseFloat(cols[2]),
                    co: parseFloat(cols[3]),
                    no2: parseFloat(cols[4]),
                    o3: parseFloat(cols[5]),
                    so2: parseFloat(cols[6]),
                    pm2_5: parseFloat(cols[7]),
                    pm10: parseFloat(cols[8])
                };
            })
            .filter(d => !isNaN(d.aqi));
        
        updateCharts('daily');
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function filterData(timeRange) {
    const now = luxon.DateTime.now();
    const selectedCity = document.getElementById('citySelect').value;
    
    return allData.filter(d => 
        d.city === selectedCity && 
        (timeRange === 'daily' ? d.timestamp >= now.minus({days: 1}) :
         timeRange === 'weekly' ? d.timestamp >= now.minus({weeks: 1}) :
         d.timestamp >= now.minus({months: 1}))
    );
}

function updateCharts(timeRange) {
    const data = filterData(timeRange);
    const labels = data.map(d => d.timestamp.toFormat('dd/MM HH:mm'));
    
    // Update AQI Chart
    if (aqiChart) aqiChart.destroy();
    aqiChart = new Chart(document.getElementById('aqiChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'AQI Index',
                data: data.map(d => d.aqi),
                borderColor: '#ff6384',
                tension: 0.1
            }]
        }
    });

    // Update Pollutants Chart
    if (pollutantsChart) pollutantsChart.destroy();
    pollutantsChart = new Chart(document.getElementById('pollutantsChart'), {
        type: 'bar',
        data: {
            labels: ['CO', 'NO2', 'O3', 'SO2', 'PM2.5', 'PM10'],
            datasets: [{
                label: 'Pollutant Levels',
                data: [
                    data.reduce((sum, d) => sum + d.co, 0) / data.length,
                    data.reduce((sum, d) => sum + d.no2, 0) / data.length,
                    data.reduce((sum, d) => sum + d.o3, 0) / data.length,
                    data.reduce((sum, d) => sum + d.so2, 0) / data.length,
                    data.reduce((sum, d) => sum + d.pm2_5, 0) / data.length,
                    data.reduce((sum, d) => sum + d.pm10, 0) / data.length
                ],
                backgroundColor: [
                    '#ff9f40', '#4bc0c0', '#9966ff', 
                    '#ffcd56', '#c45850', '#36a2eb'
                ]
            }]
        }
    });
}

// Initial load
loadData();
setInterval(loadData, 300000); // Refresh data every 5 minutes
