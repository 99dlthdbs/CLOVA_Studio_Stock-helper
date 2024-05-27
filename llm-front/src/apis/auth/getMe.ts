import axios from "axios";

export const getMe = async () => {
  const res = await axios.get("/auth/me");
  return res.data;
};
