
const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

// ==========================================
// CLEAN AI-GENERATED MARKDOWN
// ==========================================

function cleanBotMessage(message) {
    let text = String(message || "");

    // Fix nested and duplicated Markdown links.
    for (let i = 0; i < 5; i++) {
        const previous = text;

        text = text.replace(
            /\[([^\]]*)\]\((https?:\/\/[^)\s]+)\)/g,
            function (_, label, url) {
                if (/^https?:\/\//i.test(label)) {
                    return url;
                }

                return `${label} (${url})`;
            }
        );

        if (text === previous) {
            break;
        }
    }

    // Remove common escaped Markdown characters.
    text = text.replace(/\\([*_[\]()])/g, "$1");

    return text.trim();
}

// ==========================================
// FORMAT BOT ANSWER SAFELY
// ==========================================

function formatBotMessage(message) {
    const content = document.createElement("div");
    content.className = "message-text";

    const text = cleanBotMessage(message);

    // Recognize URLs, Markdown links, bold text, and list markers.
    const tokenPattern =
        /https?:\/\/[^\s<>"')\]]+|\*\*[\s\S]+?\*\*|(^|\n)\s*(?:\d+[.)]\s+|[-*]\s+)/g;

    const lines = text.split("\n");
    const fragment = document.createDocumentFragment();

    let currentList = null;
    let currentListType = null;

    function closeList() {
        currentList = null;
        currentListType = null;
    }

    function appendInlineText(parent, value) {
        // Bold text and URLs are processed without using innerHTML.
        const inlinePattern =
            /\*\*(.+?)\*\*|https?:\/\/[^\s<>"')\]]+/g;

        let lastIndex = 0;
        let match;

        while ((match = inlinePattern.exec(value)) !== null) {
            parent.appendChild(
                document.createTextNode(
                    value.slice(lastIndex, match.index)
                )
            );

            if (match[0].startsWith("**")) {
                const strong = document.createElement("strong");
                strong.textContent = match[1];
                parent.appendChild(strong);
            } else {
                let url = match[0];
                let trailing = "";

                while (/[.,!?;:]$/.test(url)) {
                    trailing = url.slice(-1) + trailing;
                    url = url.slice(0, -1);
                }

                // Only allow HTTP and HTTPS links.
                if (/^https?:\/\//i.test(url)) {
                    const link = document.createElement("a");
                    link.href = url;
                    link.textContent = url;
                    link.target = "_blank";
                    link.rel = "noopener noreferrer";
                    parent.appendChild(link);
                }

                if (trailing) {
                    parent.appendChild(
                        document.createTextNode(trailing)
                    );
                }
            }

            lastIndex = match.index + match[0].length;
        }

        parent.appendChild(
            document.createTextNode(value.slice(lastIndex))
        );
    }

    function appendParagraph(value) {
        const paragraph = document.createElement("p");
        appendInlineText(paragraph, value);
        fragment.appendChild(paragraph);
    }

    for (const originalLine of lines) {
        const line = originalLine.trim();

        // Blank lines separate paragraphs or lists.
        if (!line) {
            closeList();
            continue;
        }

        // Numbered list: 1. Step or 1) Step
        const numberedMatch = line.match(/^(\d+)[.)]\s+(.+)$/);

        // Bulleted list: - Step, * Step, or • Step
        const bulletMatch = line.match(/^(?:[-*•])\s+(.+)$/);

        if (numberedMatch) {
            if (currentListType !== "ol") {
                closeList();
                currentList = document.createElement("ol");
                fragment.appendChild(currentList);
                currentListType = "ol";
            }

            const item = document.createElement("li");
            appendInlineText(item, numberedMatch[2]);
            currentList.appendChild(item);
            continue;
        }

        if (bulletMatch) {
            if (currentListType !== "ul") {
                closeList();
                currentList = document.createElement("ul");
                fragment.appendChild(currentList);
                currentListType = "ul";
            }

            const item = document.createElement("li");
            appendInlineText(item, bulletMatch[1]);
            currentList.appendChild(item);
            continue;
        }

        closeList();

        // Display ordinary text as a separate paragraph.
        appendParagraph(line);
    }

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
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Something went wrong."
            );
        }

        addMessage(
            data.answer ||
                "Sorry, I couldn't generate an answer.",
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

        const question = questions[topic];

        if (question) {
            userInput.value = question;
            userInput.focus();
        }
    });
});
