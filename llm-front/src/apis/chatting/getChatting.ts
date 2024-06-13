import { CardType, ChattingTypes } from "@/@types/ChattingTypes";
import axios from "axios";

const parsing_cards = (data: string) => {
  const cardList: CardType[] = [];
  if (!data) return cardList;

  const splitted = data.split("%T%T%");

  splitted.forEach((e) => {
    const [title, content, url] = e.split("####");
    cardList.push({ title, content, url });
  });

  return cardList;
};

export const getChatting = async (room_id: string) => {
  const res = await axios.get<ChattingTypes[]>(`/api/chatting/${room_id}`);
  const { data } = res;

  return data.map((e) => {
    const cards = parsing_cards(e.card_data);

    return {
      ...e,
      cards,
    };
  });
};
