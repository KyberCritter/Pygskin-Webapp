// Get the balance and initialize from the database
const balanceElement = document.getElementById('balance-display');
let currentBalance = parseFloat(balanceElement.getAttribute('data-credit-balance')) || 0;
let bettingHistory = [];

// Display the current balance
function updateBalanceDisplay() {
    document.getElementById('balance-display').innerText = `Balance: ${Number(currentBalance).toFixed(2).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} Credits`;
}

// These variables need to be defined here, because there are errors when the django formatted variables are defined in external JS files
// const gamesList = JSON.parse('{{ games_json|escapejs }}');
// console.log(gamesList);

// Update the betting history when a bet is placed. This could be removed if the betting history is removed from the page
function updateBettingHistory(bet) {
    bettingHistory.push(bet);

    // console.log(bet);
    // bet stores:
    // amount
    // game (same data as database)
    // odds
    // type
    // winnings

    const historyContainer = document.getElementById('betting-history');
    historyContainer.innerHTML = ''; // Clear previous content

    if (bettingHistory.length === 0) {
        historyContainer.innerHTML = '<p>No bets placed yet.</p>';
        return;
    }

    const historyList = document.createElement('ul');
    bettingHistory.forEach((item, index) => {
        const listItem = document.createElement('li');
        var value = "";
        const awayTeamDisplay = item.game.away_team === "Hawaii" ? "Hawai'i" : item.game.away_team;
        const homeTeamDisplay = item.game.home_team === "Hawaii" ? "Hawai'i" : item.game.home_team;
        if (item.type.includes('Spread Away')) {
            value += "Spread " + awayTeamDisplay + " (" + (item.game.away_money_line < 0 ? '-' : '+') + Math.abs(parseFloat(item.game.spread).toFixed(1)) + ")";
        } else if (item.type.includes('Spread Home')) {
            value += "Spread " + homeTeamDisplay + " (" + (item.game.away_money_line < 0 ? '-' : '+') + Math.abs(parseFloat(item.game.spread).toFixed(1)) + ")";
        } else if (item.type.includes('Moneyline Away')) {
            value += "Moneyline " + awayTeamDisplay;
        } else if (item.type.includes('Moneyline Home')) {
            value += "Moneyline " + homeTeamDisplay;
        } else if (item.type === 'Over') {
            value += "Total Points Over " + parseFloat(item.game.over_under).toFixed(1);
        } else if (item.type === 'Under') {
            value += "Total Points Under " + parseFloat(item.game.over_under).toFixed(1);
        }
        listItem.innerText = `Bet #${index + 1}: ${value} (${item.odds > 0 ? '+' : ''}${item.odds}) ${item.amount} Credits to win ${item.winnings} Credits`;
        historyList.appendChild(listItem);
    });

    historyContainer.appendChild(historyList);
}

const modal = document.getElementById('betModal');
const modalTitle = document.getElementById('modalTitle');
const betAmountInput = document.getElementById('betAmount');
const submitBetButton = document.getElementById('submitBetButton');
const closeModal = document.querySelector('.close-modal');
let currentBet = null;

// Calculate winnings based on the odds
function calculateWinnings(betAmount, odds) {
    if (odds > 0) {
        // Positive odds (e.g., +120 means winning $120 on a $100 bet)
        return betAmount * (odds / 100);
    } else {
        // Negative odds (e.g., -150 means winning $100 on a $150 bet)
        return betAmount / Math.abs(odds / 100);
    }
}

function openModal(betType, gameStr) {
    const game = JSON.parse(decodeURIComponent(gameStr));
    let odds = 0;

    // Determine odds based on the betType
    if (betType.includes('Spread Away')) {
        odds = parseFloat(game.away_spread_price);
        modalTitle.innerHTML = `Spread: ${game.away_team === "Hawaii" ? "Hawai'i" : game.away_team} (${game.away_money_line < 0 ? '-' : '+'}${Math.abs(parseFloat(game.spread).toFixed(1))})</br>${odds > 0 ? '+' : ''}${odds}`;
    } else if (betType.includes('Spread Home')) {
        odds = parseFloat(game.home_spread_price);
        modalTitle.innerHTML = `Spread: ${game.home_team === "Hawaii" ? "Hawai'i" : game.home_team} (${game.home_money_line < 0 ? '-' : '+'}${Math.abs(parseFloat(game.spread).toFixed(1))})</br>${odds > 0 ? '+' : ''}${odds}`;
    } else if (betType.includes('Moneyline Away')) {
        odds = parseFloat(game.away_money_line);
        modalTitle.innerHTML = `Moneyline: ${game.away_team === "Hawaii" ? "Hawai'i" : game.away_team}</br>${odds > 0 ? '+' : ''}${odds}`;
    } else if (betType.includes('Moneyline Home')) {
        odds = parseFloat(game.home_money_line);
        modalTitle.innerHTML = `Moneyline: ${game.home_team === "Hawaii" ? "Hawai'i" : game.home_team}</br>${odds > 0 ? '+' : ''}${odds}`;
    } else if (betType === 'Over') {
        odds = parseFloat(game.away_over_under_price);
        modalTitle.innerHTML = `Total Score: Over ${parseFloat(game.over_under).toFixed(1)}</br>${odds > 0 ? '+' : ''}${odds}`;
    } else if (betType === 'Under') {
        odds = parseFloat(game.home_over_under_price);
        modalTitle.innerHTML = `Total Score: Under ${parseFloat(game.over_under).toFixed(1)}</br>${odds > 0 ? '+' : ''}${odds}`;
    }

    modal.style.display = 'flex';
    currentBet = { type: betType, game: game, odds: odds }; // Store current bet details, including odds

    // Update potential winnings display
    const potentialWinningsDisplay = document.getElementById('potentialWinnings');
    if (potentialWinningsDisplay) {
        const betAmount = parseFloat(betAmountInput.value) || 0;
        const potentialWinnings = calculateWinnings(betAmount, odds) + betAmount;
        potentialWinningsDisplay.innerText = `Potential Winnings: ${potentialWinnings} Credits`;
    }
}

function closeModalFunc() {
    modal.style.display = 'none';
    betAmountInput.value = '';
    currentBet = null;
}

closeModal.addEventListener('click', closeModalFunc);

// Close modal if user clicks outside of it
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        closeModalFunc();
    }
});

// Format the date and time to display it in local time format
function formatDateTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    const now = new Date();
    const options = { hour: 'numeric', minute: 'numeric', hour12: true };
    const formattedTime = date.toLocaleTimeString([], options);

    const isToday = date.toDateString() === now.toDateString();
    const isTomorrow = date.toDateString() === new Date(now.setDate(now.getDate() + 1)).toDateString();

    if (isToday) {
        return `Today at ${formattedTime}`;
    } else if (isTomorrow) {
        return `Tomorrow at ${formattedTime}`;
    } else {
        const formattedDate = date.toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
        return `${formattedDate} at ${formattedTime}`;
    }
}

// Dynamically create a bet card for the game passed into the function
function createBetCard(game) {
    const card = document.createElement('div');
    card.classList.add('bet-card');

    // BAND-AID SOLUTION TO FIX THE ' IN HAWAII MESSING UP THE PARSERS
    if (game.away_team === "Hawai'i") {
        game.away_team = "Hawaii";
    }
    if (game.home_team === "Hawai'i") {
        game.home_team = "Hawaii";
    }


    card.innerHTML = `
            <div class="team-names">${game.away_team === "Hawaii" ? "Hawai'i" : game.away_team} @ ${game.home_team === "Hawaii" ? "Hawai'i" : game.home_team}</div>
            <div class="game-time">${formatDateTime(game.game_date)}</div>
            ${game.spread !== null && game.away_spread_price !== null && game.home_spread_price !== null ? `
            <span style="color: white">
            Point Spread
            </span>
            <div class="bet-button-container">
                    <button class="bet-button" onclick="openModal('Spread Away', '${encodeURIComponent(JSON.stringify(game))}')">
                        ${game.away_team === "Hawaii" ? "Hawai'i" : game.away_team} (${game.away_money_line < 0 ? '-' : '+'}${Math.abs(parseFloat(game.spread).toFixed(1))})</br>${game.away_spread_price > 0 ? '+' : ''}${Math.round(game.away_spread_price)}
                    </button>
                    <button class="bet-button" onclick="openModal('Spread Home', '${encodeURIComponent(JSON.stringify(game))}')">
                        ${game.home_team === "Hawaii" ? "Hawai'i" : game.home_team} (${game.home_money_line < 0 ? '-' : '+'}${Math.abs(parseFloat(game.spread).toFixed(1))})</br>${game.home_spread_price > 0 ? '+' : ''}${Math.round(game.home_spread_price)}
                    </button>
            </div>
            ` : ''}
            ${game.away_money_line !== null && game.home_money_line !== null ? `
            <span style="color: white">
            Moneyline
            </span>
            <div class="bet-button-container">
                    <button class="bet-button" onclick="openModal('Moneyline Away', '${encodeURIComponent(JSON.stringify(game))}')">
                        ${game.away_team === "Hawaii" ? "Hawai'i" : game.away_team}</br>${game.away_money_line > 0 ? '+' : ''}${Math.round(game.away_money_line)}
                    </button>
                    <button class="bet-button" onclick="openModal('Moneyline Home', '${encodeURIComponent(JSON.stringify(game))}')">
                        ${game.home_team === "Hawaii" ? "Hawai'i" : game.home_team}</br>${game.home_money_line > 0 ? '+' : ''}${Math.round(game.home_money_line)}
                    </button>
            </div>
            ` : ''}
            ${game.over_under !== null && game.away_over_under_price !== null && game.home_over_under_price !== null ? `
            <span style="color: white">
            Total Score
            </span>
            <div class="bet-button-container">
                    <button class="bet-button" onclick="openModal('Over', '${encodeURIComponent(JSON.stringify(game))}')">
                        Over ${parseFloat(game.over_under).toFixed(1)}</br>${game.away_over_under_price > 0 ? '+' : ''}${Math.round(game.away_over_under_price)}
                    </button>
                    <button class="bet-button" onclick="openModal('Under', '${encodeURIComponent(JSON.stringify(game))}')">
                        Under ${parseFloat(game.over_under).toFixed(1)}</br>${game.home_over_under_price > 0 ? '+' : ''}${Math.round(game.home_over_under_price)}
                    </button>
            </div>
            ` : ''}
        `;

    return card;
}

// sort the gamesList by date/time
gamesList.sort((a, b) => new Date(a.game_date) - new Date(b.game_date));

// create cards dynamically for each one
const container = document.getElementById('betting-container');
const currentTime = new Date();

gamesList.forEach(game => {
    const gameDate = new Date(game.game_date);
    if (gameDate > currentTime) { // do not create bet cards if the game has already started
        container.appendChild(createBetCard(game));
    }
});

// need to submit the bet data to the database here
submitBetButton.addEventListener('click', () => {
    const betAmount = parseFloat(betAmountInput.value);
    if (isNaN(betAmount) || betAmount <= 0 || !/^\d+(\.\d{1,2})?$/.test(betAmount)) {
        alert('Please enter a valid bet amount.');
        return;
    }

    if (betAmount > currentBalance) {
        alert('Insufficient balance to place this bet.');
        return;
    }

    // Construct the data to send to the server
    const betData = {
        game_id: currentBet.game.id,
        bet_type: currentBet.type,
        credits_bet: betAmount,
        odds: currentBet.odds
    };

    // Debugging output
    // console.log("Bet Data:", betData);

    // Check if any property in betData is undefined or null
    if (!betData.game_id || !betData.bet_type || !betData.credits_bet || betData.odds === undefined) {
        alert("Error: Some bet data is missing.");
        return;
    }

    var currentTimeToCheck = new Date();
    var gameDate = new Date(currentBet.game.game_date);
    if (gameDate < currentTimeToCheck) { // error for edge casing where someone could cheat and open the page, then wait to bet until after the game starts
        alert("Error: Cannot bet on a game that has already started.");
        // clear and rebuild cards
        const container = document.getElementById('betting-container');
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
        const currentTime = new Date();

        gamesList.forEach(game => {
            const gameDate = new Date(game.game_date);
            if (gameDate > currentTime) { // do not create bet cards if the game has already started
                container.appendChild(createBetCard(game));
            }
        });
        closeModalFunc();
        return;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrfToken = getCookie('csrftoken');

    // Send an AJAX POST request to submit the bet
    // THIS NEEDS TO BE IN HTML FILE (DJANGO VARIABLES DON'T WORK IN SEPARATE JS FILE)
    // const placeBetUrl = "{% url 'place_bet' %}";

    fetch(placeBetUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify(betData)
    })

        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentBalance = data.new_balance;  // Update the balance with the new value
                updateBalanceDisplay();  // Refresh the balance display

                currentBet.amount = betAmount;
                currentBet.winnings = (calculateWinnings(betAmount, currentBet.odds) + betAmount).toFixed(2);
                updateBettingHistory(currentBet);  // Add the bet to betting history
                closeModalFunc();
            } else {
                alert(data.error || "An error occurred while placing your bet.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An unexpected error occurred.");
        });
});

// Initialize balance display on page load
updateBalanceDisplay();

// Event listener to update potential winnings on input change
betAmountInput.addEventListener('input', () => {
    if (currentBet) {
        const betAmount = parseFloat(betAmountInput.value) || 0;
        if (isNaN(betAmount) || betAmount < 0 || !/^\d+(\.\d{1,2})?$/.test(betAmount) || betAmount > currentBalance) {
            betAmountInput.style.backgroundColor = '#f8d7da';
        }
        else {
            betAmountInput.style.backgroundColor = '';
        }
        const potentialWinnings = (calculateWinnings(betAmount, currentBet.odds) + betAmount).toFixed(2);
        document.getElementById('potentialWinnings').innerText = `Potential Winnings: ${potentialWinnings.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} Credits`;
    }
});