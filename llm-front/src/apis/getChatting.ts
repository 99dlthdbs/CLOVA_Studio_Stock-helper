import axios from "axios";

export const getChatting = async (room_id: string) => {
  const res = await axios.get(`/chatting/${room_id}`);

  return res.data;
};
