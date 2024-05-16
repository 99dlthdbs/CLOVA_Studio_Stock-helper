import styled from "@emotion/styled";
import { Outlet } from "react-router-dom";
import ChatList from "@/components/ChatList";

const ChatLayout = () => {
  return (
    <ChatLayoutContainer>
      <ChatListContainer>
        <ChatList />
      </ChatListContainer>
      <OutletContainer>
        <Outlet />
      </OutletContainer>
    </ChatLayoutContainer>
  );
};

export default ChatLayout;

const ChatLayoutContainer = styled.div`
  display: flex;

  width: 100%;
  height: 100vh;

  background-color: var(--bg-1);
  color: var(--theme-color-4);
`;

const ChatListContainer = styled.div`
  flex-shrink: 0;

  width: 16.25rem;
`;

const OutletContainer = styled.div`
  width: 100%;
`;
