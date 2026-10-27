const chatBox = document.getElementById("chatBox");

const userInput = document.getElementById("userInput");

const sendButton = document.getElementById("sendButton");


// ==========================================
// ADD MESSAGE TO CHAT
// ==========================================

function addMessage(message, type) {

    const messageDiv = document.createElement("div");

    messageDiv.className = `message ${type}`;


    const avatar = document.createElement("div");

    avatar.className = "avatar";

    avatar.textContent =
        type === "bot" ? "🤖" : "👤";


    const content = document.createElement("div");

    content.className = "message-content";


    const name = document.createElement("div");

    name.className = "message-name";

    name.textContent =
        type === "bot"
            ? "University Assistant"
            : "You";


    const text = document.createElement("p");

    text.textContent = message;


    content.appendChild(name);

    content.appendChild(text);


    messageDiv.appendChild(avatar);

    messageDiv.appendChild(content);


    chatBox.appendChild(messageDiv);


    chatBox.scrollTop = chatBox.scrollHeight;
}


// ==========================================
// SEND QUESTION
// ==========================================

async function sendQuestion() {

    const question = userInput.value.trim();


    if (!question) {

        return;
    }


    // Show user message

    addMessage(
        question,
        "user"
    );


    // Clear input

    userInput.value = "";


    // Disable button

    sendButton.disabled = true;

    sendButton.textContent = "Thinking...";


    try {

        const response = await fetch(
            "/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Something went wrong."
            );
        }


        // Show chatbot answer

        addMessage(
            data.answer,
            "bot"
        );


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        addMessage(
            "Sorry, something went wrong while connecting to the chatbot. Please try again.",
            "bot"
        );


    } finally {

        sendButton.disabled = false;

        sendButton.textContent = "Send";

        userInput.focus();
    }
}


// ==========================================
// SEND BUTTON
// ==========================================

sendButton.addEventListener(
    "click",
    sendQuestion
);


// ==========================================
// ENTER KEY
// ==========================================

userInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendQuestion();
        }
    }
);


// ==========================================
// TOPIC BUTTONS
// ==========================================

const topicButtons =
    document.querySelectorAll(".topic");


topicButtons.forEach(
    function(button) {

        button.addEventListener(
            "click",
            function() {

                const topic =
                    button.textContent.trim();


                const questions = {

                    "📚 Courses":
                        "What courses are available at the university?",

                    "📝 Assignments":
                        "What is my assignment deadline?",

                    "📅 Examinations":
                        "How can I check my exam date?",

                    "💰 Fees":
                        "How can I check my university fees?",

                    "📊 Attendance":
                        "What are the attendance criteria?",

                    "📋 Results":
                        "How can I check my results?",

                    "🕐 Timetable":
                        "How can I check my timetable?",

                    "📖 Library":
                        "What are the library facilities?",

                    "🏠 Hostel":
                        "What hostel facilities are available?",

                    "🎓 Scholarships":
                        "How can I find information about scholarships?"
                };


                const question =
                    questions[topic];


                if (question) {

                    userInput.value =
                        question;

                    userInput.focus();
                }
            }
        );
    }
);