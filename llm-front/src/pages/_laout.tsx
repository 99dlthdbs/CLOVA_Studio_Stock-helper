import React, { Suspense } from "react";
import { Outlet } from "react-router-dom";
import styled from "@emotion/styled";
import TypingText from "@/components/common/TypingText";

const Layout: React.FC = () => {
  return (
    <MainLayoutContainer>
      <LeftContainer>
        <TypingText
          text={
            "안녕하세요. 저는 Stockelper입니다.\n 도와드릴 것이 있다면 말씀해주세요."
          }
        />
      </LeftContainer>
      <RightContainer>
        <Suspense fallback={"loading..."}>
          <Outlet />
        </Suspense>
      </RightContainer>
    </MainLayoutContainer>
  );
};

export default Layout;

const MainLayoutContainer = styled.div`
  display: flex;
`;

const LeftContainer = styled.div`
  width: 50%;
  height: 100vh;
  flex-grow: 1;

  display: flex;
  justify-content: center;
  align-items: center;

  background-color: var(--bg-2);
`;

const RightContainer = styled.div`
  width: 50%;
  flex-grow: 1;
`;
