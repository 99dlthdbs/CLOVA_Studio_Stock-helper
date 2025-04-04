import { CardType, ChattingTypes } from "@/@types/ChattingTypes";
import SendIcon from "@/assets/icon-paper-plane.svg?react";
import styled from "@emotion/styled";
import { useCallback, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { getChatToken } from "@/apis/chatting/getChatToken";
import { formatContent } from "@/apis/chatting/getChatting";
import { createRoom } from "@/apis/room/createRoom";
import { chattingListAtoms } from "@/atom/chattingAtoms";
import { useAtom } from "jotai";
import { v4 as uuidv4 } from "uuid";

const ChatInput = () => {
  const { pathname } = useLocation();
  const navigate = useNavigate();

  const [chattingList, setChattingList] =
    useAtom<ChattingTypes[]>(chattingListAtoms);

  const cardList: CardType[] = [];

  let temp = useMemo(() => {
    return [...chattingList];
  }, [chattingList, pathname]);

  const [text, setText] = useState<string>("");

  const roomId = useMemo(() => {
    const id = pathname.split("/").pop();

    if (id === "chat") return null;
    return id;
  }, [pathname]);

  const onChangeTextAreaHandler = useCallback(
    (event: React.ChangeEvent<HTMLTextAreaElement>) => {
      const { value } = event.target;
      setText(value);
    },
    [roomId],
  );

  const onSend = useCallback(() => {
    sendMessage(roomId);
    setText("");
  }, [pathname, roomId, text, chattingList]);

  const sendMessage = (roomId: string | null | undefined) => {
    if (!roomId) {
      createRoom(text).then((e) => {
        getChatToken(e.id).then((res) => {
          const roomid = e.id;
          temp = addRequestData(temp, text, roomId || roomid);
          setChattingList(temp);

          connectWebSockect(text, roomId || roomid, res.token);
        });
      });
    } else {
      getChatToken(roomId).then((res) => {
        temp = addRequestData(temp, text, roomId);
        setChattingList(temp);

        connectWebSockect(text, roomId, res.token);
      });
    }
  };

  const onEnterHandler = useCallback(
    (event: React.KeyboardEvent) => {
      const { key, shiftKey } = event;

      if (event.nativeEvent.isComposing) {
        event.stopPropagation();
        return;
      }

      if (key === "Enter" && !shiftKey) {
        if (!text) return;

        onSend();
      }
    },
    [pathname, roomId, text, chattingList],
  );

  const connectWebSockect = (text: string, roomId: string, token: string) => {
    const prefix = import.meta.env.DEV ? "ws://" : "wss://";
    const ws = new WebSocket(`${prefix}${import.meta.env.VITE_API_URL}/infer`);
    ws.onopen = () => {
      const sendData = { msg: text, room_id: roomId, token: token };
      ws.send(JSON.stringify(sendData));
    };

    ws.onmessage = (event) => {
      const { data } = event;

      // if data start with #$#$#
      if (data.startsWith("#$#$#")) {
        const res = data.replaceAll("#$#$#", "");
        const splitted = res.split("####");
        const [title, content, url] = splitted;

        cardList.push({ title, content, url });
      } else if (data.startsWith("!@!@!")) {
        const res = data.replaceAll("!@!@!", "");
        const splitted = res.split("####");
        const [date, company, code, analysis, callSign, finance, targetFee, endFee] = splitted;

        cardList.push({
          title: `[${finance}] ${date} ${company} 분석 리포트`,
          content: formatContent(code, callSign, analysis, targetFee, endFee),
          url: "#"
        });
      } else {
        temp = addResponseData(
          temp,
          data,
          temp[temp.length - 1]!.id.toString(),
        );
        setChattingList(temp);
      }
    };

    ws.onclose = () => {
      navigate(`/chat/${roomId}`);
      ws.close();
    };
  };

  const addRequestData = (
    list: ChattingTypes[],
    requestText: string,
    roomId: string,
  ) => {
    return [
      ...list,
      {
        id: uuidv4(),
        room_id: roomId,
        chat_idx: uuidv4(),
        question: requestText,
        answer: "",
        created_at: new Date().toDateString(),
        updated_at: new Date().toDateString(),
        deleted_at: null,
      },
    ] as ChattingTypes[];
  };

  const addResponseData = (
    list: ChattingTypes[],
    eventStreamText: string,
    messageId: string,
  ) => {
    return list.map((e) => {
      if (e.id.toString() === messageId) {
        return {
          ...e,
          answer: e.answer + "\n" + eventStreamText,
          cards: cardList,
        };
      } else return e;
    });
  };

  return (
    <TextAreaContainer>
      <TextArea
        value={text}
        placeholder={"Message Stockelper..."}
        onChange={onChangeTextAreaHandler}
        onKeyDown={onEnterHandler}
      />
      <IconContainer onClick={onSend}>
        <SendIcon
          width={"1.25rem"}
          height={"1.25rem"}
          color={"var(--theme-color-2)"}
        />
      </IconContainer>
    </TextAreaContainer>
  );
};

export default ChatInput;

const TextAreaContainer = styled.div`
  width: 100%;
  display: flex;
  position: relative;
`;

const TextArea = styled.textarea`
  width: 100%;
  height: 2.8rem;
  padding: 0.75rem;

  color: var(--theme-color-4);
  font-size: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--theme-color-2);

  resize: none;

  scrollbar-width: none;

  &:focus {
    border: 1px solid var(--highlight-1);
  }

  &::placeholder {
    color: var(--theme-color-2);
  }
`;

const IconContainer = styled.div`
  position: absolute;
  right: 1rem;
  top: 0.75rem;
`;
