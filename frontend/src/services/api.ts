import axios from 'axios';
import Cookies from 'js-cookie';
axios.defaults.withCredentials = true; // Include credentials (cookies) in requests

export interface Device {
    id: number;
    name: string;
    status: boolean;
  }

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/', // Backend server
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // Include credentials (cookies) in requests
});

// apiClient.interceptors.request.use((config) => {
//     const token = Cookies.get('csrftoken'); // Get CSRF token from cookies
//     if (token) {
//         config.headers['X-CSRFToken'] = token; // Set CSRF token in headers
//     }
//     return config;
// })

// Add CSRF token to headers
apiClient.interceptors.request.use((config) => {
    const csrfToken = document.cookie
        .split('; ')
        .find((row) => row.startsWith('csrftoken='))
        ?.split('=')[1];
    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
});


export async function getDevices(): Promise<Device[]> {
    const res = await apiClient.get<Device[]>("/api/devices/");
    return res.data;
}
  
export async function toggleDeviceStatus(deviceId: number): Promise<Device> {
    const res = await apiClient.get<Device>(`/api/devices/${deviceId}/toggle/`);
    return res.data;
}

export async function getCheapestEnergyPrices(apiKey: string, productCode: string, tariffCode: string) {
    const params = new URLSearchParams({
        api_key: apiKey,
        product_code: productCode,
        tariff_code: tariffCode,
    });
    const response = await apiClient.get(`/api/cheapest-energy-slots/?${params.toString()}`);
    if (response.status !== 200) throw new Error('Failed to fetch prices');
    return response.data;
}

export default apiClient;