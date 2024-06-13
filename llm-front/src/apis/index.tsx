import axios from "axios";

export const initialAxios = () => {
  const prefix = import.meta.env.DEV ? "http://" : "https://";
  axios.defaults.baseURL = `${prefix}${import.meta.env.VITE_API_URL}`;
  axios.defaults.withCredentials = true;
};
