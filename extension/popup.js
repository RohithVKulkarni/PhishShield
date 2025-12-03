document.addEventListener('DOMContentLoaded', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = new URL(tab.url);

    document.getElementById('current-url').textContent = url.hostname;

    // In a real app, we would query the background script for the status of this tab
    // For now, we'll just show a placeholder
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = "Active & Monitoring";
    statusDiv.className = "status safe";
});
