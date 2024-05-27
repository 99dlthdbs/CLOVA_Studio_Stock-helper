import axios from "axios";
import { logInUserInfoType } from "@/types/AuthTypes";

export const login = async (userInfo: logInUserInfoType) => {
  const res = await axios.post("/auth/login", userInfo);
  return res.data;
};
