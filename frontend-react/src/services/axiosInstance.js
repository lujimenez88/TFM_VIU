
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;

export const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'ngrok-skip-browser-warning': 'true'
  }
});
