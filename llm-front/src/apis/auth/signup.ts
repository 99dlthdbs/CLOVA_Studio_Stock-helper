import axios from "axios";
import { signUpInfoType } from "@/@types/AuthTypes";

export const signup = async (signUpInfo: signUpInfoType) => {
  const res = await axios.post("/api/auth/signup", signUpInfo);
  return res.data;
};
