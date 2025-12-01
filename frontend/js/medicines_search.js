document.getElementById("search-btn").addEventListener("click", searchMedicines);

async function searchMedicines() {
    const query = document.getElementById("search-input").value.trim();
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>Searching...</p>";

    try {
        const response = await fetch(`/api/medicines?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        resultsDiv.innerHTML = "";

        if (data.results.length === 0) {
            resultsDiv.innerHTML = "<p>No results found.</p>";
            return;
        }

        data.results.forEach(med => {
            const item = document.createElement("div");
            item.classList.add("result-item");
            item.innerHTML = `
                <strong>${med.name}</strong><br>
                <small>${med.indication} — ${med.manufacturer_name}</small>
            `;

            item.style.cursor = "pointer";
            item.addEventListener("click", () => loadDetails(med.medicine_id));

            resultsDiv.appendChild(item);
        });

    } catch (err) {
        console.error(err);
        resultsDiv.innerHTML = "<p>Error.</p>";
    }
}
