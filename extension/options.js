// PhishShield AI - Options Page Script

const API_URL = "http://localhost:8000/api/v1";

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        
        // Update active tab
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Update active content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
    });
});

// Show status message
function showStatus(message, isError = false) {
    const statusEl = document.getElementById('statusMessage');
    statusEl.textContent = message;
    statusEl.className = `status-message ${isError ? 'error' : 'success'}`;
    statusEl.style.display = 'block';
    
    setTimeout(() => {
        statusEl.style.display = 'none';
    }, 5000);
}

// Load lists from API
async function loadLists() {
    try {
        const response = await fetch(`${API_URL}/lists`);
        if (!response.ok) throw new Error('Failed to load lists');
        
        const data = await response.json();
        
        // Render whitelist
        renderList('whitelist', data.whitelist);
        
        // Render blacklist
        renderList('blacklist', data.blacklist);
        
    } catch (error) {
        console.error('Error loading lists:', error);
        showStatus('Failed to load lists. Make sure the backend is running.', true);
    }
}

// Render a list
function renderList(listType, items) {
    const container = document.getElementById(`${listType}Container`);
    
    if (items.length === 0) {
        container.innerHTML = '<div class="empty-state">NO ENTRIES YET</div>';
        return;
    }
    
    container.innerHTML = items.map(item => `
        <div class="list-item">
            <div class="list-item-info">
                <div class="list-item-pattern">${escapeHtml(item.pattern)}</div>
                ${item.note ? `<div class="list-item-note">${escapeHtml(item.note)}</div>` : ''}
            </div>
            <div class="list-item-actions">
                <button class="btn btn-danger remove-btn" data-entry-id="${item.id}">REMOVE</button>
            </div>
        </div>
    `).join('');
    
    // Attach event listeners to all remove buttons
    container.querySelectorAll('.remove-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const entryId = parseInt(this.getAttribute('data-entry-id'));
            await removeEntry(entryId);
        });
    });
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Remove entry
async function removeEntry(entryId) {
    if (!confirm('Are you sure you want to remove this entry?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/lists/${entryId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to remove entry');
        
        showStatus('✓ Entry removed successfully');
        loadLists();
        
    } catch (error) {
        console.error('Error removing entry:', error);
        showStatus('Failed to remove entry', true);
    }
}

// Add to whitelist
document.getElementById('addWhitelist').addEventListener('click', async () => {
    const pattern = document.getElementById('whitelistPattern').value.trim();
    const note = document.getElementById('whitelistNote').value.trim();
    
    if (!pattern) {
        showStatus('Please enter a URL or domain pattern', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/lists`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                list_type: 'whitelist',
                pattern: pattern,
                note: note || null
            })
        });
        
        if (!response.ok) throw new Error('Failed to add to whitelist');
        
        showStatus('✓ Added to whitelist successfully');
        document.getElementById('whitelistPattern').value = '';
        document.getElementById('whitelistNote').value = '';
        
        loadLists();
        
    } catch (error) {
        console.error('Error adding to whitelist:', error);
        showStatus('Failed to add to whitelist', true);
    }
});

// Add to blacklist
document.getElementById('addBlacklist').addEventListener('click', async () => {
    const pattern = document.getElementById('blacklistPattern').value.trim();
    const note = document.getElementById('blacklistNote').value.trim();
    
    if (!pattern) {
        showStatus('Please enter a URL or domain pattern', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/lists`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                list_type: 'blacklist',
                pattern: pattern,
                note: note || null
            })
        });
        
        if (!response.ok) throw new Error('Failed to add to blacklist');
        
        showStatus('✓ Added to blacklist successfully');
        document.getElementById('blacklistPattern').value = '';
        document.getElementById('blacklistNote').value = '';
        
        loadLists();
        
    } catch (error) {
        console.error('Error adding to blacklist:', error);
        showStatus('Failed to add to blacklist', true);
    }
});

// Export lists
document.getElementById('exportBtn').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_URL}/lists/export?format=json`);
        if (!response.ok) throw new Error('Failed to export lists');
        
        const data = await response.json();
        
        // Download as file
        const blob = new Blob([data.data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `phishshield-lists-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        showStatus('✓ Lists exported successfully');
        
    } catch (error) {
        console.error('Error exporting lists:', error);
        showStatus('Failed to export lists', true);
    }
});

// Import lists
document.getElementById('importBtn').addEventListener('click', () => {
    document.getElementById('importFile').click();
});

document.getElementById('importFile').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    try {
        const text = await file.text();
        const format = file.name.endsWith('.csv') ? 'csv' : 'json';
        
        const response = await fetch(`${API_URL}/lists/import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                data: text,
                format: format
            })
        });
        
        if (!response.ok) throw new Error('Failed to import lists');
        
        const result = await response.json();
        showStatus(`✓ Imported ${result.imported.whitelist} whitelist and ${result.imported.blacklist} blacklist entries`);
        
        loadLists();
        
        // Reset file input
        e.target.value = '';
        
    } catch (error) {
        console.error('Error importing lists:', error);
        showStatus('Failed to import lists', true);
    }
});

// Load lists on page load
loadLists();
