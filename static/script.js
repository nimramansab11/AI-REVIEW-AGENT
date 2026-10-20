const content = document.getElementById("content");
const counter = document.getElementById("counter");
const reviewBtn = document.getElementById("reviewBtn");
const clearBtn = document.getElementById("clearBtn");

const emptyState = document.getElementById("emptyState");
const loading = document.getElementById("loading");
const result = document.getElementById("result");


// Character counter
content.addEventListener("input", () => {
    const length = content.value.length;
    counter.textContent = `${length.toLocaleString()} characters`;
});


// Review button
reviewBtn.addEventListener("click", async () => {

    const text = content.value.trim();

    if (!text) {
        alert("Please enter some content to review.");
        return;
    }

    // UI state
    emptyState.classList.add("hidden");
    result.classList.add("hidden");
    loading.classList.remove("hidden");

    reviewBtn.disabled = true;

    const buttonText = reviewBtn.querySelector("span:first-child");

    if (buttonText) {
        buttonText.textContent = "Analyzing...";
    }

    try {

        const response = await fetch("/review", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                content: text
            })
        });

        const data = await response.json();

        console.log("API Response:", data);

        if (!response.ok) {
            throw new Error(
                data.detail ||
                data.error ||
                "Review failed."
            );
        }

        // Hide loading
        loading.classList.add("hidden");

        // Show result
        result.textContent = data.review || "No review returned.";
        result.classList.remove("hidden");

    } catch (error) {

        console.error("Review Error:", error);

        loading.classList.add("hidden");

        result.textContent =
            "Something went wrong.\n\n" +
            error.message;

        result.classList.remove("hidden");

    } finally {

        reviewBtn.disabled = false;

        if (buttonText) {
            buttonText.textContent = "Analyze Content";
        }
    }
});


// Clear button
clearBtn.addEventListener("click", () => {

    content.value = "";

    counter.textContent = "0 characters";

    result.textContent = "";
    result.classList.add("hidden");

    loading.classList.add("hidden");

    emptyState.classList.remove("hidden");
});