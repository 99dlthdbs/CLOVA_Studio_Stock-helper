import styled from "@emotion/styled";

interface ButtonProps {
  theme: "light" | "dark";
  text: string;
  onClick: () => void;
}

const Button = ({ theme, text, onClick }: ButtonProps) => {
  return (
    <ButtonElement theme={theme} onClick={onClick}>
      {text}
    </ButtonElement>
  );
};

export default Button;

interface ButtonElementProps {
  theme: string;
}

const ButtonElement = styled.button<ButtonElementProps>`
  width: 100%;

  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 600;

  border: ${({ theme }) =>
    theme === "light"
      ? "1px solid var(--bg-4)"
      : "1px solid var(--theme-color-2)"};
  border-radius: 0.5rem;
  background-color: ${({ theme }) =>
    theme === "light" ? "var(--theme-color-3)" : "var(--bg-3)"};
  color: ${({ theme }) =>
    theme === "light" ? "var(--bg-1)" : "var(--theme-color-4)"};

  &:hover {
    transition: border 0.2s ease-out;
    border: 1px solid var(--highlight-1);
  }
`;
