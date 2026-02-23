const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

const request = async (endpoint, options = {}) => {
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    const headers = {
        ...options.headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    return fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });
};

export const apiClient = {
    get: (endpoint, options = {}) => request(endpoint, { ...options, method: 'GET' }),
    post: (endpoint, options = {}) => request(endpoint, { ...options, method: 'POST' }),
    put: (endpoint, options = {}) => request(endpoint, { ...options, method: 'PUT' }),
    patch: (endpoint, options = {}) => request(endpoint, { ...options, method: 'PATCH' }),
    delete: (endpoint, options = {}) => request(endpoint, { ...options, method: 'DELETE' }),
};

export default apiClient;
