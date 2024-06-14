import { CardType, ChattingTypes } from "@/@types/ChattingTypes";
import axios from "axios";

export const formatContent = (callSign: string, analysis: string, targetFee: string, endFee: string) => `
분석 : ${analysis}
매수 신호 : ${callSign}
목표가 : ${targetFee} 원
종가 : ${endFee} 원 
`

const parsing_cards = (data: string) => {
  const cardList: CardType[] = [];
  if (!data) return cardList;

  const splitted = data.split("%T%T%");

  splitted.forEach((e) => {
    if (e.startsWith("#$#$#")) {
      const [title, content, url] = e.replaceAll("#$#$#", "")
        .trim()
        .split("####");
      cardList.push({ title, content, url });
    } else if (e.startsWith("!@!@!")) {
      const [date, company, code, analysis, callSign, finance, targetFee, endFee] = e.replaceAll("!@!@!", "")
        .trim()
        .split("####");

      cardList.push({
        title: `[${finance}] ${date} ${company} 분석 리포트`,
        content: formatContent(callSign, analysis, targetFee, endFee),
        url: "#"
      });
    }
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
