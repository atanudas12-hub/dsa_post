document.addEventListener('DOMContentLoaded', () => {

    // --- Authentication Logic ---
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const showSignup = document.getElementById('show-signup');
    const showLogin = document.getElementById('show-login');
    const authError = document.getElementById('auth-error');

    if (loginForm && signupForm) {
        showSignup.addEventListener('click', (e) => {
            e.preventDefault();
            loginForm.classList.add('hidden');
            loginForm.classList.remove('active');
            signupForm.classList.remove('hidden');
            signupForm.classList.add('active');
            authError.classList.add('hidden');
        });

        showLogin.addEventListener('click', (e) => {
            e.preventDefault();
            signupForm.classList.add('hidden');
            signupForm.classList.remove('active');
            loginForm.classList.remove('hidden');
            loginForm.classList.add('active');
            authError.classList.add('hidden');
        });

        async function handleAuth(url, data) {
            try {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await res.json();

                if (result.success) {
                    window.location.href = result.redirect;
                } else {
                    authError.textContent = result.message;
                    authError.classList.remove('hidden');
                }
            } catch (err) {
                authError.textContent = 'Connection Error. Try again.';
                authError.classList.remove('hidden');
            }
        }

        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            handleAuth('/api/login', { username, password });
        });

        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('signup-username').value;
            const password = document.getElementById('signup-password').value;
            handleAuth('/api/signup', { username, password });
        });
    }

    // --- Dashboard Logic ---
    const postForm = document.getElementById('post-form');
    const feedContainer = document.querySelector('.feed-container');

    if (feedContainer) {
        loadPosts();
    }

    if (postForm) {
        postForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const urlInput = document.getElementById('leetcode-url');
            const url = urlInput.value;

            try {
                const res = await fetch('/api/posts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                const result = await res.json();

                if (result.success) {
                    urlInput.value = ''; // Clear input
                    loadPosts(); // Reload feed
                } else {
                    alert(result.message);
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    async function loadPosts() {
        if (!feedContainer) return;

        try {
            const res = await fetch('/api/posts');
            const data = await res.json();

            feedContainer.innerHTML = ''; // Clear current feed

            if (data.posts.length === 0) {
                feedContainer.innerHTML = '<div class="glass-panel" style="padding:1rem; text-align:center; color:#888;">No signals yet. Be the first to broadcast.</div>';
                return;
            }

            data.posts.forEach((post, index) => {
                const date = new Date(post.timestamp).toLocaleDateString() + ' ' + new Date(post.timestamp).toLocaleTimeString();

                const card = document.createElement('div');
                card.className = 'post-card';
                card.style.animationDelay = `${index * 0.1}s`; // Staggered animation

                card.innerHTML = `
                    <div class="post-header">
                        <span class="username">@${post.username}</span>
                        <span class="timestamp">${date}</span>
                    </div>
                    <div class="post-content">
                        <a href="${post.url}" target="_blank">📄 ${post.url}</a>
                    </div>
                `;
                feedContainer.appendChild(card);
            });

        } catch (err) {
            console.error('Failed to sync feed', err);
        }
    }
});
