function covidUpdate(recovered, delta, time) {
    content = recovered;
    if (delta) {
        content += ` <span id="covidDelta">(+${delta})</span>`;
    }
    document.querySelector("#covidTracker").innerHTML = `<span class="covidDataTitle">Recovered:</span><br> ${content}`;
    document.querySelector("#covidTracker").title = `Patients worldwide recovered from COVID-19 as of ${time}`;
    document.querySelector("#covidTracker").classList.remove("no-data");

}
function covidNoData(){
    document.querySelector("#covidTracker").innerHTML = "No data";
    document.querySelector("#covidTracker").title = "No data could be fetched from API";
    document.querySelector("#covidTracker").classList.add("no-data");
}