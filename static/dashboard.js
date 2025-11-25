async function fetchStats() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = "Loading NFL passing yards stats...";

    try {
        const response = await fetch('/api/passing_yards');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        let html = "<table><tr><th>Player</th><th>Team</th><th>Yards</th></tr>";
        for (const player of data.players) {
            html += `<tr>
                <td>${player.name}</td>
                <td>${player.team}</td>
                <td>${player.stat}</td>
            </tr>`;
        }
        html += "</table>";
        resultsDiv.innerHTML = html;
    } catch (error) {
        resultsDiv.innerHTML = "Error loading stats: " + error;
    }
}
