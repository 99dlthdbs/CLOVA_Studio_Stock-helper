

export interface CardType {
  title: string;
  content: string;
  url: string;
}

export type ChattingTypes = {
  id: number;
  room_id: number;
  chat_idx: number;
  question: string;
  answer: string;
  card_data: string;
  rag_data: string;
  cards: CardType[];
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
};
