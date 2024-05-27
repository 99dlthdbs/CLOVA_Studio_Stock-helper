import styled from "@emotion/styled";
import MoreIcon from "@/assets/menu-dots-vertical.svg?react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import TrashIcon from "@/assets/trash.svg?react";
import { deleteRoom } from "@/apis/room/deleteRoom";

interface ChatListItemProps {
  title: string;
  itemId: number;
}

const ChatListItem = ({ title, itemId }: ChatListItemProps) => {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const menuRef = useRef<HTMLDivElement | null>(null);
  const [isMenuActive, setIsMenuActive] = useState<boolean>(false);

  const roomId = useMemo(() => {
    const id = pathname.split("/").pop();

    if (id === "chat") return null;
    return id;
  }, [pathname]);

  const isSelected = useMemo(() => {
    return roomId === itemId.toString();
  }, [pathname]);

  const onClickMoreHandler = useCallback(() => {
    if (roomId) {
      if (confirm("해당 메시지를 삭제하시겠습니까?")) {
        deleteRoom(roomId).then(() => {
          alert("삭제되었습니다.");
          navigate("/chat");
        });
      }
    }
  }, [pathname]);

  const onCloseModeHandler = useCallback((event: MouseEvent) => {
    const { target } = event;
    if (
      !(menuRef && menuRef.current && menuRef.current.contains(target as Node))
    ) {
      setIsMenuActive(false);
    }
  }, []);

  useEffect(() => {
    window.addEventListener("mousedown", onCloseModeHandler);

    return () => {
      window.removeEventListener("mousedown", onCloseModeHandler);
    };
  });

  return (
    <ChatListItemContainer isSelected={isSelected} ref={menuRef}>
      <Title>{title}</Title>
      <OverlayBox isSelected={isSelected} />
      {isSelected && (
        <>
          <MoreContainer
            onClick={() => {
              setIsMenuActive((prev) => !prev);
            }}
            // onClick={onClickMoreHandler}
          >
            <MoreIcon
              width={"1.25rem"}
              height={"1.25rem"}
              color={"var(--theme-color-3)"}
            />
          </MoreContainer>
          {isMenuActive && (
            <MenuContainer onClick={onClickMoreHandler}>
              <TrashIcon width={"1rem"} height={"1rem"} />
              delete
            </MenuContainer>
          )}
        </>
      )}
    </ChatListItemContainer>
  );
};

export default ChatListItem;

interface ChatListItemContainerProps {
  isSelected: boolean;
}

const ChatListItemContainer = styled.div<ChatListItemContainerProps>`
  display: flex;
  align-items: center;

  position: relative;

  padding: 1rem;

  border: 1px solid rgba(0, 0, 0, 0);
  border-radius: 0.5rem;
  cursor: pointer;

  background-color: ${({ isSelected }) =>
    isSelected ? "var(--theme-color-1)" : "inherit"};

  &:hover {
    transition: border 0.5s ease-out;
    border: 1px solid var(--theme-color-3);
  }
`;

const Title = styled.p`
  display: flex;
  align-items: center;

  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.875rem;
  font-weight: 500;
`;

const OverlayBox = styled.div<ChatListItemContainerProps>`
  position: absolute;
  right: 0;

  width: 80px;
  height: 44px;

  border-radius: 8px;
  background-color: ${({ isSelected }) =>
    isSelected
      ? "linear-gradient(90deg, rgba(54, 54, 54, 0) 0%, #181422 76.4%)"
      : "inherit"};
`;

const MoreContainer = styled.div`
  position: absolute;
  top: 0.875rem;
  right: 0.5rem;

  &:hover svg circle {
    transition: fill 0.5s ease;
    fill: var(--theme-color-4);
  }
`;

const MenuContainer = styled.div`
  position: absolute;
  right: 0;
  top: 2.5rem;
  padding: 1rem;

  display: flex;
  align-items: center;
  gap: 0.25rem;

  font-size: 0.875rem;
  border-radius: 0.5rem;
  background-color: var(--theme-color-2);

  z-index: 1;
`;
