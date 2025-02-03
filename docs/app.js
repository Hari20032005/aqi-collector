// REPLACE WITH YOUR ACTUAL DATA PATH
const DATA_URL = 'https://raw.githubusercontent.com/Hari20032005/aqi-collector/main/data/aqi_data.csv';

async function init() {
    try {
        // 1. Load Data
        const response = await fetch(DATA_URL);
        if (!response.ok) throw new Error('Failed to load data');
        const csvText = await response.text();
        
        // 2. Parse Data
        const data = csvText.split('\n')
            .slice(1)
            .filter(row => row.trim())
            .map(row => {
                const [city, timestamp, aqi] = row.split(',');
                return {
                    city: city,
                    date: new Date(timestamp),
                    aqi: parseFloat(aqi)
                };
            });
        
        // 3. Create Chart
        const ctx = document.getElementById('aqiChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => `${d.date.toLocaleDateString()} ${d.date.toLocaleTimeString()}`),
                datasets: [{
                    label: 'AQI Index',
                    data: data.map(d => d.aqi),
                    borderColor: '#4CAF50',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: { title: { display: true, text: 'Time' } },
                    y: { title: { display: true, text: 'AQI' } }
                }
            }
        });
        
    } catch (error) {
        console.error('Initialization failed:', error);
        document.body.innerHTML = `<div class="error">Error loading data: ${error.message}</div>`;
    }
}

// Start the application
init();
