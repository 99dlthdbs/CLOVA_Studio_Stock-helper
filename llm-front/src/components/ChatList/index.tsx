import styled from "@emotion/styled";
import ChartIcon from "@/assets/icon-chart-line-up.svg?react";
import ChatListItem from "@/components/ChatList/ChatListItem";
import UserInfo from "@/components/ChatList/UserInfo";
import { useCallback, useEffect, useRef, useState } from "react";

import { RoomListTypes } from "@/@types/RoomTypes";
import { useLocation, useNavigate } from "react-router-dom";
import { getRoomList } from "@/apis/room/getRoomList";

const ChatList = () => {
  const { pathname } = useLocation();
  const listRef = useRef<HTMLDivElement | null>(null);
  const [roomList, setRoomList] = useState<RoomListTypes[] | null>();

  const navigate = useNavigate();

  useEffect(() => {
    getRoomList().then((e) => {
      setRoomList(e);
    });
  }, [pathname]);

  const onClickRoomListItemHandler = useCallback(
    (id: number) => {
      navigate(`/chat/${id}`);
    },
    [roomList],
  );

  const onClickNewChatHandler = useCallback(() => {
    navigate("/chat");
  }, [navigate]);

  return (
    <ChatContainer ref={listRef}>
      <TitleContainer>
        <ChartIcon
          width={"1.5rem"}
          height={"1.5rem"}
          fill={"var(--theme-color-4)"}
        />
        <Title>Stockelper</Title>
      </TitleContainer>
      <NewChatContainer onClick={onClickNewChatHandler}>
        <IconContainer>🎉</IconContainer>
        <NewChatText>New Chat</NewChatText>
      </NewChatContainer>
      <ChatListContainer>
        {roomList &&
          roomList.map((e) => {
            return (
              <div
                key={e.id}
                onClick={() => {
                  onClickRoomListItemHandler(e.id);
                }}
              >
                <ChatListItem itemId={e.id} title={e.name} />
              </div>
            );
          })}
      </ChatListContainer>
      <UserInfo name={"정영상"} />
    </ChatContainer>
  );
};
export default ChatList;

const ChatContainer = styled.div`
  width: 100%;
  height: 100vh;

  padding: 0.875rem 0.75rem;

  background-color: var(--bg-4);
  color: var(--theme-color-4);

  overflow: hidden;
`;

const TitleContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;

  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;

  &:hover {
    transition: background-color 0.5s ease-out;
    background-color: var(--theme-color-1);
  }
`;

const Title = styled.h1`
  font-size: 1rem;
  font-weight: 500;
`;

const NewChatContainer = styled.div`
  display: flex;
  gap: 0.5rem;

  padding: 0.75rem;

  font-size: 0.875rem;
  font-weight: 500;

  border-radius: 0.5rem;
  cursor: pointer;

  &:hover {
    transition: background-color 0.5s ease-out;
    background-color: var(--theme-color-1);
  }
`;

const NewChatText = styled.p``;

const IconContainer = styled.div``;

const ChatListContainer = styled.div`
  height: calc(100vh - 10.5rem);
  position: relative;
`;
