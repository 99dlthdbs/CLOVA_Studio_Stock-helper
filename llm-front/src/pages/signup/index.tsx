import Input from "@/components/common/Input";
import Button from "@/components/common/Button";
import styled from "@emotion/styled";
import { useNavigate } from "react-router-dom";
import { useCallback, useState } from "react";
import { signup } from "@/apis/auth/signup";

const Signup = () => {
  const navigate = useNavigate();
  const [userInfo, setUserInfo] = useState({
    nickname: "",
    email: "",
    password: "",
  });

  const onClickSignupHandler = useCallback(async () => {
    const result = await signup(userInfo);
    if (result.id) {
      alert("회원가입 성공");

      navigate("/login");
    }
  }, [userInfo, navigate]);

  const onClickLogInHandler = useCallback(() => {
    navigate("/login");
  }, [navigate]);

  const onChangeValueHandler = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>, currKey: string) => {
      const { value } = event.target;

      if (value === null) return;

      if (currKey === "email") {
        setUserInfo((prev) => {
          return {
            ...prev,
            email: value,
          };
        });
      } else if (currKey === "password") {
        setUserInfo((prev) => {
          return {
            ...prev,
            password: value,
          };
        });
      } else if (currKey === "name") {
        setUserInfo((prev) => {
          return {
            ...prev,
            nickname: value,
          };
        });
      }
    },
    [],
  );

  const onEnterHandler = useCallback(
    async (event: React.KeyboardEvent<HTMLInputElement>) => {
      const { keyCode } = event;
      if (keyCode === 13) {
        await onClickSignupHandler();
      }
    },
    [userInfo],
  );

  return (
    <SignupContainer>
      <TitleText>Signup</TitleText>
      <InputContainer>
        <Input
          placeholder={"name"}
          type={"string"}
          value={userInfo.nickname}
          onChange={onChangeValueHandler}
          onEnter={onEnterHandler}
        />
        <Input
          placeholder={"email"}
          type={"string"}
          value={userInfo.email}
          onChange={onChangeValueHandler}
          onEnter={onEnterHandler}
          icon={"user"}
        />
        <Input
          placeholder={"password"}
          type={"password"}
          value={userInfo.password}
          onChange={onChangeValueHandler}
          onEnter={onEnterHandler}
          icon={"password"}
        />
      </InputContainer>
      <ButtonContainer>
        <Button
          theme={"light"}
          text={"SIGNUP"}
          onClick={onClickSignupHandler}
        />
        <Button theme={"dark"} text={"LOGIN"} onClick={onClickLogInHandler} />
      </ButtonContainer>
    </SignupContainer>
  );
};

export default Signup;

const SignupContainer = styled.div`
  width: 100%;
  height: 100vh;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;

  background-color: var(--theme-color-1);
`;

const TitleText = styled.h1`
  font-size: 2rem;
  font-weight: 600;
  color: var(--theme-color-4);
`;

const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  width: 20rem;
`;

const ButtonContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  width: 20rem;
`;
