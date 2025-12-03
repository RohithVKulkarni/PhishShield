// Configuration
const API_URL = "http://localhost:8000/api/v1/score";
const BLOCK_PAGE_URL = chrome.runtime.getURL("block.html");

// Cache for recent URLs to avoid redundant checks
const urlCache = new Map();

chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    if (details.frameId !== 0) return; // Only check main frame

    const url = details.url;
    if (url.startsWith("chrome://") || url.startsWith("about:") || url === BLOCK_PAGE_URL) return;

    console.log(`Checking URL: ${url}`);

    // Check cache first
    if (urlCache.has(url)) {
        const result = urlCache.get(url);
        if (result.is_phishing) {
            chrome.tabs.update(details.tabId, { url: `${BLOCK_PAGE_URL}?url=${encodeURIComponent(url)}` });
        }
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            console.error("API Error:", response.statusText);
            return;
        }

        const data = await response.json();
        console.log("Scan Result:", data);

        // Cache the result
        urlCache.set(url, data);

        if (data.is_phishing) {
            chrome.tabs.update(details.tabId, { url: `${BLOCK_PAGE_URL}?url=${encodeURIComponent(url)}&reason=${encodeURIComponent(data.reasons.join(", "))}` });
        }

    } catch (error) {
        console.error("Network Error:", error);
    }
});
