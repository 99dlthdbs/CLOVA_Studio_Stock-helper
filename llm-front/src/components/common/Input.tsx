import styled from "@emotion/styled";
import UserIcon from "@/assets/icon-user.svg?react";
import PasswordIcon from "@/assets/lock.svg?react";
import EyeIcon from "@/assets/eye.svg?react";
import EyeCrossIcon from "@/assets/eye-crossed.svg?react";
import { useCallback, useState } from "react";

interface InputProps {
  placeholder: string;
  icon?: string;
  type: string;
  value: string;
  onChange: (
    event: React.ChangeEvent<HTMLInputElement>,
    currKey: string,
  ) => void;
}

const Input = ({ placeholder, value, onChange, type, icon }: InputProps) => {
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const [isFocus, setIsFocus] = useState<boolean>(false);

  const onClickVisibleHandler = useCallback(() => {
    setIsVisible((prev) => !prev);
  }, []);

  const onFocusHandler = useCallback(() => {
    setIsFocus(true);
  }, []);

  const onBlurHandler = useCallback(() => {
    setIsFocus(false);
  }, []);

  return (
    <InputContainer>
      <InputElement
        placeholder={placeholder}
        type={"password" ? (isVisible ? "string" : type) : type}
        value={value}
        onFocus={onFocusHandler}
        onBlur={onBlurHandler}
        onChange={(event) => onChange(event, placeholder)}
        icon={!!icon}
        password={type === "password"}
      />
      {icon && (
        <LeftContainer>
          <IconContainer>
            {icon === "user" && (
              <UserIcon
                width={"1.25rem"}
                height={"1.25rem"}
                color={isFocus ? "var(--highlight-1)" : "var(--theme-color-2)"}
              />
            )}
            {icon === "password" && (
              <PasswordIcon
                width={"1.25rem"}
                height={"1.25rem"}
                color={isFocus ? "var(--highlight-1)" : "var(--theme-color-2)"}
              />
            )}
          </IconContainer>
        </LeftContainer>
      )}
      {type === "password" && (
        <VisibleContainer onClick={onClickVisibleHandler}>
          {isVisible ? (
            <IconContainer>
              <EyeIcon
                width={"1.25rem"}
                height={"1.25rem"}
                color={isFocus ? "var(--highlight-1)" : "var(--theme-color-2)"}
              />
            </IconContainer>
          ) : (
            <IconContainer>
              <EyeCrossIcon
                width={"1.25rem"}
                height={"1.25rem"}
                color={isFocus ? "var(--highlight-1)" : "var(--theme-color-2)"}
              />
            </IconContainer>
          )}
        </VisibleContainer>
      )}
    </InputContainer>
  );
};

export default Input;

interface InputElementProps {
  icon: boolean;
  password: boolean;
}

const InputContainer = styled.div`
  width: 100%;

  position: relative;
`;

const InputElement = styled.input<InputElementProps>`
  width: 100%;
  padding: ${({ icon, password }) =>
    icon
      ? password
        ? "0.75rem 0.75rem 0.75rem 2.5rem"
        : "0.75rem 2.5rem"
      : "0.75rem"};

  border-radius: 0.5rem;
  border: 1px solid var(--theme-color-2);
  color: var(--theme-color-4);

  &::placeholder {
    color: var(--theme-color-2);
  }

  &:focus {
    transition: 0.2s ease-out;
    border: 1px solid var(--highlight-1);
  }
`;

const IconContainer = styled.div`
  line-height: 0;
  width: fit-content;
  height: fit-content;
`;

const LeftContainer = styled.div`
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
`;

const VisibleContainer = styled.div`
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
`;
