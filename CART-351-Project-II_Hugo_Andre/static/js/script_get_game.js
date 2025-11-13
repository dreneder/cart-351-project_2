//Accessing the survey form with javascript - detecting when the form is submitted
window.onload = function () {

    // this variable will manage which question is displayed
    let qStage = 0;
    let currentAnswers = []; // cache of top answers for current stage
    let score = 0; // running tally

        // gets the game container by id
        const gameContainer = document.getElementById("gameContainer");
        const instructions = document.getElementById("instructions");
        // hides the board when the stage is 0 or 4 (beginning and end)
        const updateBoardVisibility = () => {
            if (!gameContainer) return;
            if (qStage === 0 || qStage === 4) {
                gameContainer.style.display = "none";
            } else {
                gameContainer.style.display = "";
            }
        };
         // hide it on load
        updateBoardVisibility();

        // functions to show and hide the form uppon submiting
        const hideGameForm = () => {
            const form = document.getElementById("ffGameFETCH");
            if (form) form.style.display = "none";
        };

        const showGameForm = () => {
            const form = document.getElementById("ffGameFETCH");
            if (form) form.style.display = "";
        };

        const questions = window.gameQuestions || {}; // passed in from Flask template
        const questionEl = document.getElementById("question");
        const scoreEl = document.getElementById("score");
        const cardsToShow = 4;

        const updateScoreDisplay = () => {
            if (scoreEl) {
                scoreEl.textContent = score;
            }
        };
        updateScoreDisplay();

        const resetCards = () => { // put every card back face-down
            for (let i = 1; i <= cardsToShow; i += 1) {
                const cardEl = document.getElementById(`card_${i}`);
                if (cardEl) {
                    cardEl.classList.remove("flip");
                    updateBoardVisibility();
                }
            }
        };

        function showBigX() { // flashy strike indicator
            const x = document.createElement("div")
            x.textContent = "X"
            x.style.position = "fixed"
            x.style.top = "50%"
            x.style.left = "50%"
            x.style.transform = "translate(-50%, -50%)"
            x.style.fontSize = "10rem"
            x.style.fontWeight = "bold"
            x.style.color = "red"
            x.style.zIndex = "9999"
            x.style.pointerEvents = "none"
            document.body.appendChild(x)
            setTimeout(() => x.remove(), 1500)
            }

        const updateQuestionText = () => { // swap the prompt when stage advances
            if (!questionEl) return;
            const questionKey = `question${Math.max(qStage - 1, 0)}`;
            questionEl.textContent = questions[questionKey] || `Question ${qStage}`;
        };

        async function loadResponses() { // pull freshest survey data for the current question
            if (qStage === 0) return;
            currentAnswers = [];
            updateQuestionText();

            try {
                const response = await fetch("/getDataFromGame");
                if (!response.ok) throw new Error("Failed to load data.json");
                const data = await response.json();
                
                const topRep = data
                .filter(item => item.Question === `q${qStage}`)
                .sort((a, b) => b.Count - a.Count)
                .slice(0, cardsToShow);
                
                currentAnswers = topRep.map(({ Response, Count }, index) => {
                    const parsedCount = Number(Count) || 0;
                    const normalized = (Response || "").toString().trim().toUpperCase();
                    const responseEl = document.getElementById(`res_${index + 1}`);
                    const countEl = document.getElementById(`count_${index + 1}`);
                    if (responseEl) responseEl.textContent = Response;
                    if (countEl) countEl.textContent = parsedCount;
                    return {
                        normalized,
                        display: Response,
                        count: parsedCount,
                        index,
                        revealed: false,
                    };
                });

                for (let i = currentAnswers.length + 1; i <= cardsToShow; i += 1) {
                    const responseEl = document.getElementById(`res_${i}`);
                    const countEl = document.getElementById(`count_${i}`);
                    if (responseEl) responseEl.textContent = "-";
                    if (countEl) countEl.textContent = "0";
                }
            } catch (err) {
                console.error("Error loading JSON", err);
            }
        }
        
        
        // the function for the next button
        const nextButton = document.querySelector(".nextButton");
        if (nextButton) {
            nextButton.addEventListener("click", () => {
                qStage += 1; // increments to the stage
                if (qStage > 0) {
                    if (instructions) instructions.style.display = "none";
                }

                if (qStage === 4) { // final screen
                    if (gameContainer) gameContainer.style.display = "none";
                    document.querySelector("#gameover").innerHTML += `<h1 style="font-size:3rem;text-align:center;">GAME OVER<br>You scored ${score} points</h1>`
                    nextButton.textContent = "Try Again";
                    qStage = 4;
                    return;
                }
        
                if (qStage === 5) { // clicking to reset page state
                    window.location.reload();
                    return;
                }
                resetCards();
                showGameForm();
                // nextButton.disabled = true;
                console.log(`stage: ${qStage}`);
                // nextButton.disabled = false;
                setTimeout(() => {
                    loadResponses(); // so the user doesn't see thenew responses
                }, 500);
            updateBoardVisibility();
            });
        }



    console.log("Loaded script_get_game.js");
    
    const game = document.querySelector("#ffGameFETCH");
    if (game) {
        game.addEventListener(

        "submit", function(event) {

            event.preventDefault();
            if (qStage === 0) {
                game.reset();
                return;
            }

            hideGameForm(); // stop spam answers until we evaluate the guess

            //Using inbuilt JavaScript FormData object to get data from the form using the form ID. 
            const gameData = new FormData(game);
            const attemptRaw = gameData.get("attempt") || "";
            const attempt = attemptRaw.toString().trim().toUpperCase();

            if (!attempt) {
                game.reset();
                return;
            }

            const match = currentAnswers.find(entry => entry.normalized === attempt); // only match exact string

            if (!match) {
                console.log("No match for attempt: ", attempt);
                game.reset();
                showBigX();
                return;
            }

            if (match.revealed) {
                game.reset();
                return;
            }

            match.revealed = true;
            score += match.count;
            updateScoreDisplay();

            const cardEl = document.getElementById(`card_${match.index + 1}`); // flip the revealed card
            if (cardEl) {
                cardEl.classList.add("flip");
            }

            //Resets the form to clear out user responses after each submit - "event.target" is the HTML form.
            event.target.reset();

        }

    )
    }

}
