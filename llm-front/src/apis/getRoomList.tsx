import axios from "axios";

export const getRoomList = async () => {
  const res = await axios.get("/room", {
    params: {
      skip: 0,
      limit: 100,
    },
  });
  return res.data;
};
