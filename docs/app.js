// Replace with your GitHub username and repo name
const DATA_URL = 'https://raw.githubusercontent.com/Hari20032005/aqi-collector/main/data/aqi_data.csv';
async function loadData() {
    try {
        const response = await fetch(DATA_URL);
        const csvData = await response.text();
        
        const rows = csvData.split('\n').slice(1);
        const data = rows.map(row => {
            const cols = row.split(',');
            return {
                city: cols[0],
                timestamp: cols[1],
                aqi: parseFloat(cols[2])
            };
        }).filter(d => !isNaN(d.aqi));

        createChart(data);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function createChart(data) {
    const ctx = document.getElementById('aqiChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.timestamp),
            datasets: [{
                label: 'AQI Index',
                data: data.map(d => d.aqi),
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour'
                    }
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Initial load
loadData();
