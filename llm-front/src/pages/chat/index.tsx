import { ChattingTypes } from "@/@types/ChattingTypes";
import { getChatting } from "@/apis/chatting/getChatting";
import { chattingListAtoms } from "@/atom/chattingAtoms";
import ChatInput from "@/components/ChatRoom/ChatInput";
import Message from "@/components/ChatRoom/Message";
import styled from "@emotion/styled";
import { useAtom } from "jotai";
import { Fragment, useCallback, useEffect, useMemo, useRef } from "react";
import { useLocation } from "react-router-dom";

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
                  <NewsCardDiv>
                    {
                      e.cards && e.cards.map((card, idx) => (
                        <NewsCard onClick={
                          () => location.href = card.url
                        }>
                          <NewsCardTitle>{card.title}</NewsCardTitle>
                          <NewsCardContent>{card.content}</NewsCardContent>
                        </NewsCard>
                      ))
                    }
                  </NewsCardDiv>
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

const NewsCard = styled.div`
  flex-shrink: 0;
  width: fit-content;
  max-width: 300px;
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 0.5rem;
  :hover {
    background: rgba(255, 255, 255, 0.2);
    cursor: pointer;
  }
`

const NewsCardTitle = styled.div`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
`

const NewsCardContent = styled.div`
  font-size: 0.75rem;
  font-weight: 400;
`

const NewsCardDiv = styled.div`
  display: flex;
  overflow-x: scroll;
  height: fit-content;
  gap: 1rem;
`;

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
