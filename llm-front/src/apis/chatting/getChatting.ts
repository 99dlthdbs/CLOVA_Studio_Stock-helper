import { CardType, ChattingTypes } from "@/@types/ChattingTypes";
import axios from "axios";

const parsing_cards = (data: string) => {
  const cardList: CardType[] = [];
  const splitted = data.split("%T%T%");

  splitted.forEach((e) => {
    const [title, content, url] = e.split("####");
    cardList.push({ title, content, url });
  });

  return cardList;
}

export const getChatting = async (room_id: string) => {
  const res = await axios.get<ChattingTypes[]>(`/api/chatting/${room_id}`);
  const { data } = res;

  const new_data = data.map((e) => {
    const cards = parsing_cards(e.card_data);
    console.log(e.card_data);
    return {
      ...e,
      cards,
    };
  });


  console.log(new_data);

  return new_data;
};
