import axios from "axios";

export const deleteRoom = async (room_id: string) => {
  const res = await axios.delete(`/room/${room_id}`);
  return res.data;
};
