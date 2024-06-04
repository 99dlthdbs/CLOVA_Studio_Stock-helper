import axios from "axios";
import { signUpInfoType } from "@/types/AuthTypes";

export const signup = async (signUpInfo: signUpInfoType) => {
  const res = await axios.post("/auth/signup", signUpInfo);
  return res.data;
};
