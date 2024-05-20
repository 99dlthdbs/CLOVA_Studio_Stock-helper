import styled from "@emotion/styled";
import Button from "@/components/common/Button";
import { useCallback } from "react";
import { useNavigate } from "react-router-dom";

const Main = () => {
  const navigate = useNavigate();

  const onClickLogInHandler = useCallback(() => {
    navigate("/login");
  }, []);

  const onClickSignUpHandler = useCallback(() => {
    navigate("/signup");
  }, []);

  return (
    <MainContainer>
      <IconContainer></IconContainer>
      <TitleText>Stockelper</TitleText>
      <ButtonContainer>
        <Button theme={"light"} text={"LOGIN"} onClick={onClickLogInHandler} />
        <Button theme={"dark"} text={"SIGNUP"} onClick={onClickSignUpHandler} />
      </ButtonContainer>
    </MainContainer>
  );
};

export default Main;

const MainContainer = styled.div`
  width: 100%;
  height: 100vh;
  background-color: var(--theme-color-1);

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 2rem;
`;

const TitleText = styled.h1`
  color: var(--theme-color-4);
  font-weight: 600;
`;

const IconContainer = styled.div`
  line-height: 0;
  width: fit-content;
  height: fit-content;
`;

const ButtonContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  width: 20rem;
`;
