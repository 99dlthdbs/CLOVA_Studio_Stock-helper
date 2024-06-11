import axios from "axios";

interface IGetChatToken {
  token: string;
  user_id: number;
  expires_at: string;
  created_at: string;
}

export const getChatToken = async (room_id: string) => {
  const res = await axios.get<IGetChatToken>(`/api/chatting/token/${room_id}`);

  return res.data;
};
