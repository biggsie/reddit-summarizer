// State
let subreddits = [];
let preferences = {};

// API Helpers
async function fetchAPI(endpoint, options = {}) {
    const response = await fetch(`/api${endpoint}`, {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }

    return response.json();
}

// Load Data
async function loadSubreddits() {
    try {
        subreddits = await fetchAPI('/subreddits');
        renderSubreddits();
    } catch (error) {
        showAlert('Error loading subreddits: ' + error.message, 'error');
    }
}

async function loadPreferences() {
    try {
        preferences = await fetchAPI('/preferences');
        renderPreferences();
    } catch (error) {
        showAlert('Error loading preferences: ' + error.message, 'error');
    }
}

// Render Functions
function renderSubreddits() {
    const list = document.getElementById('subreddit-list');

    if (subreddits.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <p>No subreddits added yet</p>
                <p style="font-size: 12px; margin-top: 8px;">Add your first subreddit above</p>
            </div>
        `;
        return;
    }

    list.innerHTML = subreddits.map(sub => `
        <li class="subreddit-item">
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="subreddit-name">r/${sub.name}</span>
                    <span class="badge ${sub.enabled ? 'badge-enabled' : 'badge-disabled'}">
                        ${sub.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                </div>
                <div class="subreddit-stats">
                    Min: ${sub.min_upvotes} upvotes, ${sub.min_comments} comments
                </div>
            </div>
            <div class="subreddit-actions">
                <button class="btn btn-small btn-secondary" onclick="toggleSubreddit(${sub.id})">
                    ${sub.enabled ? 'Disable' : 'Enable'}
                </button>
                <button class="btn btn-small btn-danger" onclick="deleteSubreddit(${sub.id})">
                    Delete
                </button>
            </div>
        </li>
    `).join('');
}

function renderPreferences() {
    document.getElementById('email-input').value = preferences.email_address || '';
    document.getElementById('digest-time').value = preferences.digest_time || '06:00';
    document.getElementById('posts-count').value = preferences.posts_per_digest || 12;
}

// Subreddit Actions
async function addSubreddit() {
    const input = document.getElementById('subreddit-input');
    const name = input.value.trim().replace('r/', '');

    if (!name) {
        showAlert('Please enter a subreddit name', 'error');
        return;
    }

    try {
        await fetchAPI('/subreddits', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                min_upvotes: 50,
                min_comments: 5
            })
        });

        input.value = '';
        await loadSubreddits();
        showAlert(`r/${name} added successfully`, 'success');
    } catch (error) {
        showAlert('Error adding subreddit: ' + error.message, 'error');
    }
}

async function deleteSubreddit(id) {
    if (!confirm('Are you sure you want to remove this subreddit?')) {
        return;
    }

    try {
        await fetchAPI(`/subreddits/${id}`, { method: 'DELETE' });
        await loadSubreddits();
        showAlert('Subreddit removed', 'success');
    } catch (error) {
        showAlert('Error removing subreddit: ' + error.message, 'error');
    }
}

async function toggleSubreddit(id) {
    try {
        await fetchAPI(`/subreddits/${id}/toggle`, { method: 'PATCH' });
        await loadSubreddits();
        showAlert('Subreddit updated', 'success');
    } catch (error) {
        showAlert('Error updating subreddit: ' + error.message, 'error');
    }
}

// Preferences Actions
async function savePreferences() {
    const email = document.getElementById('email-input').value;
    const digestTime = document.getElementById('digest-time').value;
    const postsCount = parseInt(document.getElementById('posts-count').value);

    try {
        await fetchAPI('/preferences', {
            method: 'PUT',
            body: JSON.stringify({
                email_address: email,
                digest_time: digestTime,
                posts_per_digest: postsCount
            })
        });

        await loadPreferences();
        showAlert('Preferences saved', 'success');
    } catch (error) {
        showAlert('Error saving preferences: ' + error.message, 'error');
    }
}

// Email Actions
async function sendTestEmail() {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Sending...';

    try {
        const result = await fetchAPI('/test-email', { method: 'POST' });
        showAlert(result.message, 'success');
    } catch (error) {
        showAlert('Error sending test email: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function generatePreview() {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Generating...';

    try {
        const result = await fetchAPI('/send-preview', { method: 'POST' });
        showAlert(`Preview sent! ${result.post_count} posts included.`, 'success');
    } catch (error) {
        showAlert('Error generating preview: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function sendDigestNow() {
    if (!confirm('Send digest now? This will mark posts as sent.')) {
        return;
    }

    const btn = event.target;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Sending...';

    try {
        const result = await fetchAPI('/send-digest', { method: 'POST' });
        showAlert(result.message, 'success');
    } catch (error) {
        showAlert('Error sending digest: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// UI Helpers
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadSubreddits();
    loadPreferences();

    // Enter key support for adding subreddit
    document.getElementById('subreddit-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addSubreddit();
        }
    });
});
