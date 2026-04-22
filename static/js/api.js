const API_BASE = '/api';

const api = {
    setTokens: (access, refresh) => {
        localStorage.setItem('access_token', access);
        if (refresh) localStorage.setItem('refresh_token', refresh);
    },

    getAccessToken: () => localStorage.getItem('access_token'),
    getRefreshToken: () => localStorage.getItem('refresh_token'),

    clearTokens: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },

    request: async (endpoint, options = {}) => {
        const token = api.getAccessToken();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers,
        };

        if (options.body instanceof FormData) {
            delete config.headers['Content-Type'];
        }

        try {
            let response = await fetch(`${API_BASE}${endpoint}`, config);

            if (response.status === 401 && api.getRefreshToken()) {
                const refreshed = await api.refreshToken();
                if (refreshed) {
                    config.headers['Authorization'] = `Bearer ${api.getAccessToken()}`;
                    response = await fetch(`${API_BASE}${endpoint}`, config);
                } else {
                    window.location.href = '/login/';
                }
            }
            return response;
        } catch (err) {
            console.error('API Error:', err);
            throw err;
        }
    },

    refreshToken: async () => {
        const refresh = api.getRefreshToken();
        if (!refresh) return false;
        try {
            const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh }),
            });
            if (res.ok) {
                const data = await res.json();
                api.setTokens(data.access);
                return true;
            }
        } catch (e) { console.error(e); }
        api.clearTokens();
        return false;
    }
};
