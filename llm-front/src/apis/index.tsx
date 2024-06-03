import axios from "axios";

export const initialAxios = () => {
  axios.defaults.baseURL = `http://${import.meta.env.VITE_API_URL}`;
  axios.defaults.withCredentials = true;
};
