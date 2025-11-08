//Accessing the survey form with javascript - detecting when the form is submitted
window.onload = function () {

    console.log("Loaded script_get.js");

    const survey = document.querySelector("#ffSurveyFETCH")

    survey.addEventListener(
        
        "submit", async function(event) {

            event.preventDefault();
            console.log("Button clicked");

            //Using inbuilt JavaScript FormData object to get data from the form using the form ID. 
            const surveyData = new FormData(survey);
            const queryParams = new URLSearchParams(surveyData).toString();
            const url = `/getDataFromForm?${queryParams}`;

            //This is the fetch request, held in a try/catch clause
            try{

                const res = await fetch(url, { method: "GET" });
                const resJSON = await res.json()
                console.log("Response JSON: ", res.json)

                document.querySelector("#results").innerHTML =
                `<br><br><h2>SURVEY SAYS.......</h2>`;
                
                if (resJSON.q_1 == ""){
                    document.querySelector("#results").innerHTML += `<i>The data you have entered for Question 1 is invalid.</i><br><br>`
                }

                else{
                    document.querySelector("#results").innerHTML += `<p> You use a <b>${resJSON.q_1}</b> first thing in the morning. Fascinating!</p><br>`

                }

                if (resJSON.q_2 == ""){
                    document.querySelector("#results").innerHTML += `<i>The data you have entered for Question 2 is invalid.</i><br><br>`
                }

                else{
                    document.querySelector("#results").innerHTML += `<p> You believe <b>${resJSON.q_2}</b> is the most fitting day to file your taxes. Diabolical!</p><br>`

                }

                if (resJSON.q_3 == ""){
                    document.querySelector("#results").innerHTML += `<i>The data you have entered for Question 3 is invalid.</i><br><br><br>`
                }

                else{
                    document.querySelector("#results").innerHTML += `<p> You would like to visit <b>${resJSON.q_3}</b> more than any other country. To each their own!</p><br><br>`

                }
                
            }

            document.querySelector("#results").innerHTML += `Data added successfully!<br><br><br>`

            catch(err){

                console.log(err)

            }

        }

    )

}
