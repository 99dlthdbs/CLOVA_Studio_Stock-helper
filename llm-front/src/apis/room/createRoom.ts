import axios from "axios";

export const createRoom = async () => {
  const res = await axios.post("/api/room", {
    name: "chat room 12",
  });

  return res.data;
};
