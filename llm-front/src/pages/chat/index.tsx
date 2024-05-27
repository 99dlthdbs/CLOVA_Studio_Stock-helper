import styled from "@emotion/styled";
import Message from "@/components/ChatRoom/Message";
import ChatInput from "@/components/ChatRoom/ChatInput";
import { Fragment, useCallback, useEffect, useMemo, useRef } from "react";
import { useLocation } from "react-router-dom";
import { ChattingTypes } from "@/types/ChattingTypes";
import { useAtom } from "jotai";
import { chattingListAtoms } from "@/atom/chattingAtoms";
import { getChatting } from "@/apis/chatting/getChatting";

const Chat = () => {
  const { pathname } = useLocation();
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [chattingList, setChattingList] =
    useAtom<ChattingTypes[]>(chattingListAtoms);

  const roomId = useMemo(() => {
    const id = pathname.split("/").pop();

    if (id === "chat") return null;
    return id;
  }, [pathname]);

  const scrollToBottomHandler = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chattingList]);

  useEffect(() => {
    if (roomId) {
      getChatting(roomId).then((e) => {
        setChattingList(e);
      });
    } else {
      setChattingList([]);
    }
  }, [pathname]);

  useEffect(() => {
    scrollToBottomHandler();
  }, [chattingList]);

  return (
    <ChatContainer>
      <ChatWrapper>
        <MessageListContainer ref={scrollRef}>
          {chattingList.length !== 0 ? (
            chattingList.map((e) => {
              return (
                <Fragment key={e.id}>
                  <Message role={"user"} content={e.question} />
                  <Message role={"assistant"} content={e.answer} />
                </Fragment>
              );
            })
          ) : (
            <p>채팅을 입력해주세요</p>
          )}
        </MessageListContainer>
        <ChatInputContainer>
          <ChatInput />
          <WarningText>
            Stockelper can make mistakes. Consider checking important
            information.
          </WarningText>
        </ChatInputContainer>
      </ChatWrapper>
    </ChatContainer>
  );
};
export default Chat;

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`;

const ChatWrapper = styled.div`
  min-width: 40rem;
  max-width: 60rem;
  width: 70%;
  height: 100vh;
  position: relative;
`;

const MessageListContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;

  height: calc(100vh - 8rem);
  padding-top: 2rem;

  overflow-y: scroll;
  overflow-x: hidden;
  scrollbar-width: none;
`;

const ChatInputContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;

  width: 100%;
  padding-top: 1rem;

  position: absolute;
  bottom: 1rem;

  background-color: var(--bg-1);
`;

const WarningText = styled.p`
  color: var(--theme-color-3);
  font-size: 0.75rem;
`;
