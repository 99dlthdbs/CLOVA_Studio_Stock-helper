import axios from "axios";

export const createRoom = async (title: string) => {
  const res = await axios.post("/api/room", {
    name: title.slice(0, 20),
  });

  return res.data;
};
