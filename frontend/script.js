
const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

// ==========================================
// FORMAT BOT ANSWER SAFELY
// ==========================================

function formatBotMessage(message) {
    const content = document.createElement("div");
    content.className = "message-text";

    let text = String(message || "");

    // Clean malformed Markdown links.
    // Example: [URL](URL) becomes URL.
    for (let i = 0; i < 5; i++) {
        text = text.replace(
            /\[([^\]]*)\]\((https?:\/\/[^)\s]+)\)/g,
            function (_, label, url) {
                return /^https?:\/\//i.test(label)
                    ? url
                    : `${label} (${url})`;
            }
        );
    }

    // Remove Markdown formatting characters left by the AI.
    text = text
        .replace(/\\([*_[\]()])/g, "$1")
        .replace(/\*\*(.*?)\*\*/g, "$1")
        .replace(/(^|[\s])\*([^*\n]+)\*/g, "$1$2");

    // Convert HTTP(S) URLs into safe clickable links.
    const urlPattern = /https?:\/\/[^\s<>"')\]]+/g;
    const fragment = document.createDocumentFragment();

    let lastIndex = 0;
    let match;

    while ((match = urlPattern.exec(text)) !== null) {
        let url = match[0];
        let trailing = "";

        // Keep punctuation outside the URL.
        while (/[.,!?;:]$/.test(url)) {
            trailing = url.slice(-1) + trailing;
            url = url.slice(0, -1);
        }

        fragment.appendChild(
            document.createTextNode(
                text.slice(lastIndex, match.index)
            )
        );

        if (url) {
            const link = document.createElement("a");
            link.href = url;
            link.textContent = url;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            fragment.appendChild(link);
        }

        fragment.appendChild(
            document.createTextNode(trailing)
        );

        lastIndex = match.index + match[0].length;
    }

    fragment.appendChild(
        document.createTextNode(text.slice(lastIndex))
    );

    content.appendChild(fragment);
    return content;
}

// ==========================================
// ADD MESSAGE TO CHAT
// ==========================================

function addMessage(message, type) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = type === "bot" ? "🤖" : "👤";

    const content = document.createElement("div");
    content.className = "message-content";

    const name = document.createElement("div");
    name.className = "message-name";
    name.textContent =
        type === "bot" ? "University Assistant" : "You";

    content.appendChild(name);

    if (type === "bot") {
        content.appendChild(formatBotMessage(message));
    } else {
        const text = document.createElement("p");
        text.textContent = message;
        content.appendChild(text);
    }

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

    if (!question || sendButton.disabled) {
        return;
    }

    addMessage(question, "user");
    userInput.value = "";

    sendButton.disabled = true;
    sendButton.textContent = "Thinking...";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Something went wrong."
            );
        }

        addMessage(
            data.answer || "Sorry, I couldn't generate an answer.",
            "bot"
        );
    } catch (error) {
        console.error("Chat error:", error);

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

sendButton.addEventListener("click", sendQuestion);

// ==========================================
// ENTER KEY
// ==========================================

userInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendQuestion();
    }
});

// ==========================================
// TOPIC BUTTONS
// ==========================================

const topicButtons = document.querySelectorAll(".topic");

topicButtons.forEach(function(button) {
    button.addEventListener("click", function() {
        const topic = button.textContent.trim();

        const questions = {
            "📚 Courses": "What courses are available at the university?",
            "📝 Assignments": "What is my assignment deadline?",
            "📅 Examinations": "How can I check my exam date?",
            "💰 Fees": "How can I check my university fees?",
            "📊 Attendance": "What are the attendance criteria?",
            "📋 Results": "How can I check my results?",
            "🕐 Timetable": "How can I check my timetable?",
            "📖 Library": "What are the library facilities?",
            "🏠 Hostel": "What hostel facilities are available?",
            "🎓 Scholarships": "How can I find information about scholarships?"
        };

        const question = questions[topic];

        if (question) {
            userInput.value = question;
            userInput.focus();
        }
    });
});
